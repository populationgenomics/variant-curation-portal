# Generated by Django 2.2.24 on 2023-01-12 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curation_portal", "0011_curationresult_flag_untranslated_transcript"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_essential_splice_rescue",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_homopolymer",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_in_frame_exon",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_last_exon",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_long_exon",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_low_pext",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_other_transcript_error",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_possible_splice_site_rescue",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_skewed_ab",
        ),
        migrations.RemoveField(
            model_name="curationresult",
            name="flag_weak_gene_conservation",
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_allele_balance",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_complex_event",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_complex_other",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_complex_splicing",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_dubious_other",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_dubious_read_alignment",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_dubious_str_or_low_complexity",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_escapes_nmd",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_flow_chart_overridden",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_frame_restoring_indel",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_gc_rich",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_homopolymer_or_str",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_in_frame_sai",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_inconsequential_transcript",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_low_genotype_quality",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_low_read_depth",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_low_truncated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_low_umap_m50",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_methionine_resuce",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_mismapped_read",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_multiple_annotations",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_rescue",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_second_opinion_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_self_chain",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_str_or_low_complexity",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="curationresult",
            name="flag_stutter",
            field=models.BooleanField(default=False),
        ),
    ]
