from collections import Counter, defaultdict

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator
from rest_framework.fields import CharField
from rest_framework.serializers import (
    ChoiceField,
    ListSerializer,
    ModelSerializer,
    RegexField,
    RelatedField,
    DictField,
    ValidationError,
)

from curation_portal.models import (
    CurationAssignment,
    CurationResult,
    CustomFlag,
    CustomFlagCurationResult,
    Project,
    User,
    UserSettings,
    Variant,
    VariantAnnotation,
    VariantTag,
    FLAG_FIELDS,
    FLAG_SHORTCUTS,
)
from curation_portal.constants import RANKED_CONSEQUENCE_TERMS
from curation_portal.verdict import validate_result_verdict

VARIANT_ID_REGEX = r"^(\d+|X|Y)[-:]([0-9]+)[-:]([ACGT]+)[-:]([ACGT]+)$"


class UserSettingsSerializer(ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ("ucsc_username", "ucsc_session_name_grch37", "ucsc_session_name_grch38")


class UserField(RelatedField):
    fail_if_not_found = False
    default_error_messages = {"invalid": "Invalid username."}

    queryset = User.objects.all()

    def to_internal_value(self, data):
        # These match the validators applied to Django's default User model's username field.
        for validator in [
            MaxLengthValidator(150, "Ensure this field has no more than 150 characters."),
            UnicodeUsernameValidator(),
        ]:
            validator(data)

        try:
            if self.fail_if_not_found:
                user = self.get_queryset().get(username=data)
            else:
                user, _ = self.get_queryset().get_or_create(username=data)
            return user
        except (TypeError, ValueError, User.DoesNotExist):
            self.fail("invalid")

    def to_representation(self, value):
        return value.username


class StrictUserField(UserField):
    fail_if_not_found = True


class ProjectSerializer(ModelSerializer):
    owners = UserField(many=True, allow_empty=False)

    class Meta:
        model = Project
        fields = ("id", "name", "owners")

    def validate_owners(self, value):
        if self.context["request"].user not in value:
            raise ValidationError("You may not remove yourself as a project owner.")

        return value


def get_xpos(chrom, pos):
    if chrom == "X":
        chrom_number = 23
    elif chrom == "Y":
        chrom_number = 24
    elif chrom == "M":
        chrom_number = 25
    else:
        chrom_number = int(chrom)

    return chrom_number * 1_000_000_000 + pos


def variant_id_parts(variant_id):
    [chrom, pos, ref, alt] = variant_id.split("-")
    pos = int(pos)
    xpos = get_xpos(chrom, pos)
    return {"chrom": chrom, "pos": pos, "xpos": xpos, "ref": ref, "alt": alt}


class VariantAnnotationSerializer(ModelSerializer):
    class Meta:
        model = VariantAnnotation
        exclude = ("id", "variant")

    def validate_consequence(self, value):
        for csq in value.split("&"):
            if csq not in set(RANKED_CONSEQUENCE_TERMS):
                raise ValidationError(
                    f"Unsupported VEP consequence term '{csq}'. Update this application to "
                    + "support the latest VEP consequence terms and their ranking relative to "
                    + "other terms. A restriction has been placed on this field to ensure that "
                    + "the major consequence of a variant can be reported to curators via the UI "
                    + "accurately."
                )

        return value


class VariantTagSerializer(ModelSerializer):
    class Meta:
        model = VariantTag
        exclude = ("id", "variant")


class VariantListSerializer(ListSerializer):  # pylint: disable=abstract-method
    def validate(self, attrs):
        # Check that all variant IDs in the list are unique
        variant_id_counts = Counter(variant_data["variant_id"] for variant_data in attrs)
        duplicate_variant_ids = [k for k, v in variant_id_counts.items() if v > 1]
        if duplicate_variant_ids:
            raise ValidationError(f"Duplicate variants with IDs {', '.join(duplicate_variant_ids)}")

        return attrs


class VariantSerializer(ModelSerializer):
    variant_id = RegexField(VARIANT_ID_REGEX, required=True)

    annotations = VariantAnnotationSerializer(many=True, required=False)
    tags = VariantTagSerializer(many=True, required=False)

    class Meta:
        model = Variant
        exclude = ("project", "chrom", "pos", "xpos", "ref", "alt")
        list_serializer_class = VariantListSerializer

    def validate(self, attrs):
        variant_id = attrs["variant_id"]

        if Variant.objects.filter(variant_id=variant_id, project=self.context["project"]).exists():
            raise ValidationError("Variant already exists in project")

        return attrs

    def create(self, validated_data):
        annotations_data = validated_data.pop("annotations", None)
        tags_data = validated_data.pop("tags", None)

        variant_id = validated_data["variant_id"]
        variant = Variant.objects.create(
            **validated_data, **variant_id_parts(variant_id), project=self.context["project"]
        )

        if annotations_data:
            annotations = [VariantAnnotation(**item, variant=variant) for item in annotations_data]
            VariantAnnotation.objects.bulk_create(annotations)

        if tags_data:
            tags = [VariantTag(**item, variant=variant) for item in tags_data]
            VariantTag.objects.bulk_create(tags)

        return variant


class CustomFlagSerializer(ModelSerializer):
    class Meta:
        model = CustomFlag
        fields = ("id", "key", "label", "shortcut")

    def validate_key(self, value):
        key = value
        if key:
            key = str(value).lower()

        existing_flag = CustomFlag.objects.filter(key=key).first()
        is_self = existing_flag and self.instance and (existing_flag.id == self.instance.id)
        if key and ((key in set(FLAG_FIELDS)) or (existing_flag and not is_self)):
            raise ValidationError(f"A flag with the identifier '{key}' already exists")

        return value  # return original value for further validation

    def validate_shortcut(self, value):
        shortcut = value
        if shortcut:
            shortcut = str(value).upper()

        if shortcut.upper().startswith("S"):
            raise ValidationError(
                "Shortcut cannot start with 'S' since it is used as the shortcut to save a "
                "curation result."
            )

        existing_flag = CustomFlag.objects.filter(shortcut=shortcut).first()
        is_self = existing_flag and self.instance and (existing_flag.id == self.instance.id)
        if shortcut and (
            (shortcut in set(FLAG_SHORTCUTS.values())) or (existing_flag and not is_self)
        ):
            raise ValidationError(f"A flag with the shortcut '{shortcut}' already exists")

        return value  # return original value for further validation


class CustomFlagCurationResultSerializer(DictField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages[
            "not_found"
        ] = "A flag with identifier '{flag_identifier}' does not exist."

    def get_default(self):
        default = super().get_default()
        if not default:
            return {f.key: False for f in CustomFlag.objects.all()}
        return default

    def get_initial(self):
        initial = super().get_initial()
        if not initial:
            return {f.key: False for f in CustomFlag.objects.all()}
        return initial

    def to_representation(self, value):
        flags_related_to_curation_result = getattr(value, "all", lambda: [])()
        flags = {c.flag.key: c.checked for c in flags_related_to_curation_result}

        for flag in CustomFlag.objects.all():
            if flag.key not in flags:
                flags[flag.key] = False

        return flags

    def create(self, result, data):
        for flag, checked in data.items():
            if not CustomFlag.objects.filter(key=flag).exists():
                self.fail("not_found", flag_identifier=flag)

            flag = result.custom_flags.filter(flag__key=flag).first()
            if flag:
                flag.checked = checked
                flag.save()
            else:
                CustomFlagCurationResult.objects.create(
                    flag=CustomFlag.objects.get(key=flag),
                    result=result,
                    checked=checked,
                )

        return result


class ImportedResultListSerializer(ListSerializer):  # pylint: disable=abstract-method
    def validate(self, attrs):
        # Check that all curator/variant ID pairs in the list are unique
        assignment_counts = Counter(
            (variant_data["curator"], variant_data["variant_id"]) for variant_data in attrs
        )
        duplicate_assignments = [k for k, v in assignment_counts.items() if v > 1]
        if duplicate_assignments:
            duplicates_by_curator = defaultdict(list)
            for curator, variant_id in duplicate_assignments:
                duplicates_by_curator[curator].append(variant_id)

            raise ValidationError(
                "Duplicate results for "
                + ", ".join(
                    f"{curator} (variants {', '.join(variants)})"
                    for curator, variants in duplicates_by_curator.items()
                )
            )

        return attrs

    def get_assignment(self, variant_id, curator):
        return CurationAssignment.objects.filter(
            variant__project=self.child.context["project"],
            variant__variant_id=variant_id,
            curator__username=curator,
        ).first()

    def save(self, **kwargs):
        """
        Save and return a list of object instances.
        """
        # Guard against incorrect use of `serializer.save(commit=False)`
        assert "commit" not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        validated_data = [{**attrs, **kwargs} for attrs in self.validated_data]
        instances = []
        for attrs in validated_data:
            instance = self.get_assignment(attrs["variant_id"], attrs["curator"])
            if instance and instance.result:
                attrs.pop("created_at", None)
                attrs.pop("updated_at", None)
                instance = self.child.update(instance.result, attrs)
                assert instance is not None, "`update()` did not return an object instance."
            else:
                instance = self.child.create(attrs)
                assert instance is not None, "`create()` did not return an object instance."

            instances.append(instance)

        return instances


class ImportedResultSerializer(ModelSerializer):
    # Dev Note: Keep these fields in-sync with ../assets/results-schema.json and also with
    # ExportedResultSerializer below.
    curator = UserField(required=True)
    variant_id = RegexField(VARIANT_ID_REGEX, required=True)

    verdict = ChoiceField(
        ["lof", "likely_lof", "uncertain", "likely_not_lof", "not_lof"],
        required=False,
        allow_null=True,
    )

    custom_flags = CustomFlagCurationResultSerializer(required=False, allow_null=True)

    class Meta:
        model = CurationResult
        exclude = ("id", "editor")
        list_serializer_class = ImportedResultListSerializer

    def validate_variant_id(self, value):
        if not Variant.objects.filter(project=self.context["project"], variant_id=value).exists():
            raise ValidationError("Variant does not exist")

        return value

    def validate(self, attrs):
        data = super().validate(attrs)
        validate_result_verdict(data)

        return data

    def create(self, validated_data):
        curator = validated_data.pop("curator", None)
        variant_id = validated_data.pop("variant_id", None)
        custom_flags = validated_data.pop("custom_flags", {})

        variant = Variant.objects.get(project=self.context["project"], variant_id=variant_id)
        # Assignment might already exist but a curation result has not yet been created.
        assignment = CurationAssignment.objects.get_or_create(curator=curator, variant=variant)[0]
        result = CurationResult(**validated_data)

        # If a created/updated timestamp is specified, override the auto_now settings on
        # CurationResult
        for field in result._meta.local_fields:
            if field.name in ["created_at", "updated_at"] and field.name in validated_data:
                field.auto_now = False
                field.auto_now_add = False

        result.save()
        if custom_flags:
            # Will throw error unless CustomFlag instance already exists.
            self.fields["custom_flags"].create(result=result, data=custom_flags)

        assignment.result = result
        assignment.save()

        return result

    def update(self, instance, validated_data):
        curator = validated_data.pop("curator", None)
        variant_id = validated_data.pop("variant_id", None)
        custom_flags = validated_data.pop("custom_flags", {})

        variant = Variant.objects.get(project=self.context["project"], variant_id=variant_id)
        assignment = CurationAssignment.objects.get(curator=curator, variant=variant)
        result = assignment.result

        # Only save the result if any of the fields have changed.
        result_changed = False
        for attr, value in validated_data.items():
            if getattr(result, attr) != value:
                result_changed = True
                setattr(result, attr, value)

        if result_changed:
            result.save()

        for flag_key, checked in custom_flags.items():
            flag = result.custom_flags.get(flag__key__exact=flag_key)
            if flag.checked != checked:
                result_changed = True
                flag.checked = checked
                flag.save()

        if result_changed and result.assignment.curator != self.context["request"].user:
            result.editor = self.context["request"].user
            result.save()

            assignment.result = result
            assignment.save()

        return result


class ExportedResultSerializer(ModelSerializer):
    # Dev Note: Keep these fields in-sync with ../assets/results-schema.json and also with
    # ImportedResultSerializer above.
    curator = CharField(source="assignment.curator.username")
    variant_id = CharField(source="assignment.variant.variant_id")
    custom_flags = CustomFlagCurationResultSerializer(required=False, allow_null=True)
    editor = UserField(required=False, allow_null=True)

    class Meta:
        model = CurationResult
        exclude = ("id",)
