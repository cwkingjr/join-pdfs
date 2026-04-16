"""Tests for processor module."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from join_pdfs.models import OrganizationFiles
from join_pdfs.processor import (
    consolidate_files,
    extract_organization_parts,
    group_files_by_organization,
)


def create_test_pdf(name: str, page_count: int = 1) -> bytes:
    """Create a minimal valid PDF with specified page count."""
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()


class TestExtractOrganizationParts:
    def test_basic_format(self):
        assert extract_organization_parts("10 - Report") == (10, "Report")

    def test_with_extra_whitespace(self):
        assert extract_organization_parts("10    -    Report") == (10, "Report")

    def test_with_additional_suffix(self):
        assert extract_organization_parts("10 - Report extra") == (10, "Report extra")

    def test_with_multiple_words_in_suffix(self):
        assert extract_organization_parts("10 - Report notes details") == (
            10,
            "Report notes details",
        )

    def test_with_spaces_in_name(self):
        assert extract_organization_parts("10 - African Vegan on a Budget") == (
            10,
            "African Vegan on a Budget",
        )

    def test_with_underscores_in_name(self):
        assert extract_organization_parts("10 - My_Report_Name") == (
            10,
            "My_Report_Name",
        )


class TestGroupFilesByOrganization:
    def test_empty_folder(self, tmp_path: Path):
        result = group_files_by_organization(tmp_path)
        assert result == []

    def test_single_organization(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report extra.pdf").touch()
        (tmp_path / "10 - Report notes.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        assert result[0].name == "Report"
        assert result[0].base_file.name == "10 - Report.pdf"
        assert len(result[0].child_files) == 2

    def test_multiple_organizations(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report notes.pdf").touch()
        (tmp_path / "20 - Invoice.pdf").touch()
        (tmp_path / "20 - Invoice details.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 2
        org_names = {org.name for org in result}
        assert org_names == {"Report", "Invoice"}

    def test_files_without_children(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        assert result[0].name == "Report"
        assert result[0].child_files == []

    def test_non_pdf_files_ignored(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report.txt").touch()
        (tmp_path / "Readme.md").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        assert result[0].name == "Report"

    def test_shortest_name_is_primary(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report extra.pdf").touch()
        (tmp_path / "10 - Report extra more details.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        assert result[0].base_file.name == "10 - Report.pdf"

    def test_underscores_dont_affect_primary_selection(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report_extra.pdf").touch()
        (tmp_path / "10 - Report extra.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        assert result[0].base_file.name == "10 - Report.pdf"

    def test_secondary_files_sorted_alphabetically(self, tmp_path: Path):
        (tmp_path / "10 - Report.pdf").touch()
        (tmp_path / "10 - Report zzz.pdf").touch()
        (tmp_path / "10 - Report aaa.pdf").touch()

        result = group_files_by_organization(tmp_path)

        assert len(result) == 1
        child_names = [f.name for f in result[0].child_files]
        assert sorted(child_names) == child_names


class TestConsolidateFiles:
    def test_consolidate_base_only(self, tmp_path: Path):
        base_file = tmp_path / "10 - Report.pdf"
        base_file.write_bytes(create_test_pdf("Report", page_count=2))

        output_folder = tmp_path / "output"
        org = OrganizationFiles(
            id=10,
            name="Report",
            base_file=base_file,
            child_files=[],
        )

        result = consolidate_files(org, output_folder)

        assert result.exists()
        reader = PdfReader(result)
        assert len(reader.pages) == 2

    def test_consolidate_with_children(self, tmp_path: Path):
        base_file = tmp_path / "10 - Report.pdf"
        base_file.write_bytes(create_test_pdf("Report", page_count=1))

        child1 = tmp_path / "10 - Report extra.pdf"
        child1.write_bytes(create_test_pdf("Extra", page_count=2))

        child2 = tmp_path / "10 - Report notes.pdf"
        child2.write_bytes(create_test_pdf("Notes", page_count=3))

        output_folder = tmp_path / "output"
        org = OrganizationFiles(
            id=10,
            name="Report",
            base_file=base_file,
            child_files=[child1, child2],
        )

        result = consolidate_files(org, output_folder)

        assert result.exists()
        reader = PdfReader(result)
        assert len(reader.pages) == 6

    def test_output_folder_created(self, tmp_path: Path):
        base_file = tmp_path / "10 - Report.pdf"
        base_file.write_bytes(create_test_pdf("Report"))

        output_folder = tmp_path / "new_output"
        org = OrganizationFiles(
            id=10,
            name="Report",
            base_file=base_file,
            child_files=[],
        )

        assert not output_folder.exists()
        consolidate_files(org, output_folder)
        assert output_folder.exists()

    def test_output_filename(self, tmp_path: Path):
        base_file = tmp_path / "10 - My Report.pdf"
        base_file.write_bytes(create_test_pdf("Report"))

        output_folder = tmp_path / "output"
        org = OrganizationFiles(
            id=10,
            name="My Report",
            base_file=base_file,
            child_files=[],
        )

        result = consolidate_files(org, output_folder)
        assert result.name == "10 - My Report.pdf"
