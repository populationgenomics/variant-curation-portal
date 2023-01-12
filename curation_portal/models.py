from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch.dispatcher import receiver


class User(AbstractUser):
    assigned_variants = models.ManyToManyField(
        "Variant", through="CurationAssignment", through_fields=("curator", "variant")
    )


class UserSettings(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name="settings")

    ucsc_username = models.CharField(max_length=100, null=True, blank=True)
    ucsc_session_name = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = "user_settings"


class Project(models.Model):
    name = models.CharField(max_length=1000)
    owners = models.ManyToManyField(
        User, related_name="owned_projects", related_query_name="owned_project"
    )

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curation_project"


class Variant(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="variants", related_query_name="variant"
    )
    reference_genome = models.CharField(
        max_length=6, choices=[("GRCh37", "GRCh37"), ("GRCh38", "GRCh38")], default="GRCh37"
    )
    variant_id = models.CharField(max_length=1000)
    liftover_variant_id = models.CharField(max_length=1000, null=True, blank=True)
    chrom = models.CharField(max_length=2)
    pos = models.IntegerField()
    xpos = models.BigIntegerField()
    ref = models.CharField(max_length=1000)
    alt = models.CharField(max_length=1000)

    qc_filter = models.CharField(max_length=100, null=True, blank=True)
    AC = models.IntegerField(null=True, blank=True)
    AN = models.IntegerField(null=True, blank=True)
    AF = models.FloatField(null=True, blank=True)
    n_homozygotes = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "curation_variant"
        unique_together = ("project", "variant_id")
        ordering = ("xpos", "ref", "alt")


class VariantAnnotation(models.Model):
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name="annotations",
        related_query_name="annotation",
    )

    consequence = models.CharField(max_length=1000)
    gene_id = models.CharField(max_length=16)
    gene_symbol = models.CharField(max_length=16)
    transcript_id = models.CharField(max_length=16)

    loftee = models.CharField(max_length=2, null=True, blank=True)
    loftee_filter = models.CharField(max_length=200, null=True, blank=True)
    loftee_flags = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "curation_variant_annotation"
        unique_together = ("variant", "transcript_id")


class VariantTag(models.Model):
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="tags", related_query_name="tag"
    )

    label = models.CharField(max_length=100)
    value = models.CharField(max_length=1000)

    class Meta:
        db_table = "curation_variant_tag"


class CurationAssignment(models.Model):
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name="curation_assignments",
        related_query_name="curation_assignment",
    )
    curator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="curation_assignments",
        related_query_name="curation_assignment",
    )
    result = models.OneToOneField(
        "CurationResult", null=True, on_delete=models.SET_NULL, related_name="assignment"
    )

    class Meta:
        db_table = "curation_assignment"
        unique_together = ("variant", "curator")


@receiver(post_delete, sender=CurationAssignment)
def delete_assignment_result(sender, instance, *args, **kwargs):  # pylint: disable=unused-argument
    if instance.result:
        instance.result.delete()


class CurationResult(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Flags
    ## Technical
    flag_no_read_data = models.BooleanField(default=False)
    flag_reference_error = models.BooleanField(default=False)
    ### Mapping errors
    flag_mapping_error = models.BooleanField(default=False)
    flag_self_chain = models.BooleanField(default=False)
    flag_str_or_low_complexity = models.BooleanField(default=False)
    flag_low_umap_m50 = models.BooleanField(default=False)
    #### Dubious read alignment
    flag_dubious_read_alignment = models.BooleanField(default=False)
    flag_mismapped_read = models.BooleanField(default=False)
    flag_complex_event = models.BooleanField(default=False)
    flag_stutter = models.BooleanField(default=False)
    flag_dubious_str_or_low_complexity = models.BooleanField(default=False)
    flag_dubious_other = models.BooleanField(default=False)
    ### Genotyping errors
    flag_genotyping_error = models.BooleanField(default=False)
    flag_low_genotype_quality = models.BooleanField(default=False)
    flag_low_read_depth = models.BooleanField(default=False)
    flag_allele_balance = models.BooleanField(default=False)
    flag_gc_rich = models.BooleanField(default=False)
    flag_homopolymer_or_str = models.BooleanField(default=False)
    flag_strand_bias = models.BooleanField(default=False)

    ## Impact
    ### Inconsequential transcript
    flag_inconsequential_transcript = models.BooleanField(default=False)
    flag_multiple_annotations = models.BooleanField(default=False)
    flag_pext_less_than_half_max = models.BooleanField(default=False)
    flag_uninformative_pext = models.BooleanField(default=False)
    flag_minority_of_transcripts = models.BooleanField(default=False)
    flag_weak_exon_conservation = models.BooleanField(default=False)
    flag_untranslated_transcript = models.BooleanField(default=False)
    ### Rescue
    flag_rescue = models.BooleanField(default=False)
    flag_mnp = models.BooleanField(default=False)
    flag_frame_restoring_indel = models.BooleanField(default=False)
    flag_first_150_bp = models.BooleanField(default=False)
    flag_in_frame_sai = models.BooleanField(default=False)
    flag_methionine_resuce = models.BooleanField(default=False)
    flag_escapes_nmd = models.BooleanField(default=False)
    flag_low_truncated = models.BooleanField(default=False)

    ## Comment
    flag_complex_splicing = models.BooleanField(default=False)
    flag_complex_other = models.BooleanField(default=False)
    flag_second_opinion_required = models.BooleanField(default=False)
    flag_flow_chart_overridden = models.BooleanField(default=False)

    # Notes
    notes = models.TextField(null=True, blank=True)
    should_revisit = models.BooleanField(default=False)

    # Decision
    verdict = models.CharField(max_length=25, null=True)

    class Meta:
        db_table = "curation_result"


@receiver(pre_save, sender=CurationResult)
def set_additional_flags(sender, instance, *args, **kwargs):  # pylint: disable=unused-argument
    if instance:
        instance.flag_dubious_read_alignment = any(
            getattr(instance, flag)
            for flag in [
                "flag_mismapped_read",
                "flag_complex_event",
                "flag_stutter",
                "flag_dubious_str_or_low_complexity",
                "flag_dubious_other",
            ]
        )


FLAG_FIELDS = [
    ## Technical
    "flag_no_read_data",
    "flag_reference_error",
    ### Mapping errors
    "flag_mapping_error",
    "flag_self_chain",
    "flag_str_or_low_complexity",
    "flag_low_umap_m50",
    #### Dubious read alignment
    "flag_dubious_read_alignment",
    "flag_mismapped_read",
    "flag_complex_event",
    "flag_stutter",
    "flag_dubious_str_or_low_complexity",
    "flag_dubious_other",
    ### Genotyping errors
    "flag_genotyping_error",
    "flag_low_genotype_quality",
    "flag_low_read_depth",
    "flag_allele_balance",
    "flag_gc_rich",
    "flag_homopolymer_or_str",
    "flag_strand_bias",
    ## Impact
    ### Inconsequential transcript
    "flag_inconsequential_transcript",
    "flag_multiple_annotations",
    "flag_pext_less_than_half_max",
    "flag_uninformative_pext",
    "flag_minority_of_transcripts",
    "flag_weak_exon_conservation",
    "flag_untranslated_transcript",
    ### Rescue
    "flag_rescue",
    "flag_mnp",
    "flag_frame_restoring_indel",
    "flag_first_150_bp",
    "flag_in_frame_sai",
    "flag_methionine_resuce",
    "flag_escapes_nmd",
    "flag_low_truncated",
    ## Comment
    "flag_complex_splicing",
    "flag_complex_other",
    "flag_second_opinion_required",
    "flag_flow_chart_overridden",
]


FLAG_LABELS = {
    "flag_mnp": "Flag In-phase MNV",
    "flag_pext_less_than_half_max": "Flag pext < 50% max",
    "flag_uninformative_pext": "Flag uninformative pext",
    "flag_minority_of_transcripts": "Flag minority of transcripts ≤ 50%",
    "flag_self_chain": "Flag self chain > 5",
    "flag_str_or_low_complexity": "Flag STR/Low complexity",
    "flag_low_umap_m50": "Flag Umap M50 < 0.5",
    "flag_low_genotype_quality": "Flag genotype quality < 30",
    "flag_low_read_depth": "Flag read depth < 15",
    "flag_allele_balance": "Flag allele balance het. < 0.25, hom. < 0.8",
    "flag_gc_rich": "Flag GC rich +/- 50 bp",
    "flag_homopolymer_or_str": "Flag homopolymer/STR > 5",
    "flag_in_frame_sai": "Flag in-frame SAI ≥ 0.2",
    "flag_escapes_nmd": "Flag escapes NMD",
    "flag_low_truncated": "Flag < 25% truncated",
}
