"""MkDocs lifecycle hook: synchronize already-computed publication assets."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def on_pre_build(config, **kwargs):
    # Load beside this file, independently of MkDocs' import path or working dir.
    source = Path(__file__).with_name("build_docs_assets.py")
    spec = spec_from_file_location("white_lies_docs_assets", source)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build_assets(Path(config.config_file_path).resolve().parent)


def on_files(files, config, **kwargs):
    """Serve original Markdown reports as downloads rather than duplicate pages."""
    from mkdocs.structure.files import File

    class MarkdownDownload(File):
        def is_documentation_page(self):
            return False

    for original in list(files):
        if original.src_uri.startswith("assets/reports/") and original.src_uri.endswith(".md"):
            download = MarkdownDownload(
                original.src_uri, original.src_dir, original.dest_dir,
                original.use_directory_urls, inclusion=original.inclusion,
            )
            files.remove(original)
            files.append(download)
    return files
