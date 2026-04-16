"""Core PDF consolidation logic."""

import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from join_pdfs.models import OrganizationFiles

ORG_PATTERN = re.compile(r"^(\d+)\s*-\s*(.+)$")


def extract_organization_parts(filename: str) -> tuple[int, str]:
    """Extract organization ID and name from filename.

    Filename format: <integer> - <organization_name>.pdf
    """
    match = ORG_PATTERN.match(filename)
    if match:
        org_id = int(match.group(1))
        org_name = match.group(2)
        return (org_id, org_name)
    raise ValueError(f"Invalid filename format: {filename}")


def group_files_by_organization(folder: Path) -> list[OrganizationFiles]:
    """Group PDF files by their organization ID.

    Primary file = shortest filename.
    Secondary files = remaining files sorted alphabetically.
    """
    pdf_files = list(folder.glob("*.pdf"))
    organizations: dict[int, list[Path]] = {}

    for pdf in pdf_files:
        org_id, _ = extract_organization_parts(pdf.stem)
        if org_id not in organizations:
            organizations[org_id] = []
        organizations[org_id].append(pdf)

    result: list[OrganizationFiles] = []
    for org_id, files in sorted(organizations.items()):
        sorted_by_length = sorted(files, key=lambda f: len(f.stem))
        primary_file = sorted_by_length[0]
        secondary_files = sorted(sorted_by_length[1:], key=lambda f: f.name)

        _, org_name = extract_organization_parts(primary_file.stem)
        result.append(
            OrganizationFiles(
                id=org_id,
                name=org_name,
                base_file=primary_file,
                child_files=secondary_files,
            )
        )

    return result


def consolidate_files(org: OrganizationFiles, output_folder: Path) -> Path:
    """Consolidate files for an organization into a single output file."""
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"{org.id} - {org.name}.pdf"

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
