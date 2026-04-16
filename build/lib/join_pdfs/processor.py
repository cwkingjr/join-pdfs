"""Core PDF consolidation logic."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from join_pdfs.models import OrganizationFiles


def extract_organization_name(filename: str) -> str:
    """Extract organization name from filename.

    The organization name is the part before any underscore suffix.
    """
    if "_" in filename:
        return filename.rsplit("_", 1)[0]
    return filename.removesuffix(".pdf")


def group_files_by_organization(folder: Path) -> list[OrganizationFiles]:
    """Group PDF files by their organization name."""
    pdf_files = list(folder.glob("*.pdf"))
    organizations: dict[str, list[Path]] = {}

    for pdf in pdf_files:
        org_name = extract_organization_name(pdf.stem)
        if org_name not in organizations:
            organizations[org_name] = []
        organizations[org_name].append(pdf)

    result: list[OrganizationFiles] = []
    for org_name, files in organizations.items():
        base_files = [f for f in files if "_" not in f.stem]
        child_files = [f for f in files if "_" in f.stem]

        if base_files:
            result.append(
                OrganizationFiles(
                    name=org_name,
                    base_file=base_files[0],
                    child_files=child_files,
                )
            )

    return result


def consolidate_files(org: OrganizationFiles, output_folder: Path) -> Path:
    """Consolidate files for an organization into a single output file."""
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"{org.name}.pdf"

    writer = PdfWriter()

    base_reader = PdfReader(org.base_file)
    for page in base_reader.pages:
        writer.add_page(page)

    for child_file in sorted(org.child_files):
        child_reader = PdfReader(child_file)
        for page in child_reader.pages:
            writer.add_page(page)

    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path
