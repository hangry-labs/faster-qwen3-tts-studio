# Project website

The GitHub Pages overview is built directly from the root README. Translated
READMEs and Markdown documentation use the same layout. The listening gallery
keeps its own player at `/examples/`.

## Preview

With the development prerequisites from [the development guide](../docs/DEVELOPMENT.md):

```powershell
task pages
```

Open <http://127.0.0.1:9004/faster-qwen3-tts-studio/>. Press Ctrl+C to stop the
preview. `task pages-build` builds without starting the server. These tasks use
a separate Ruby Docker image and do not start the speech engine or use a GPU.
The staged build includes local public-file edits and respects Git ignore rules.

`Gemfile.lock` pins GitHub Pages 232 and its dependencies. The container uses the
same Jekyll 3.10 build as GitHub Pages, with safe mode enabled. The existing
branch-based Pages deployment can build this configuration without a separate
Actions workflow.

## Configuration

Edit the root [`_config.yml`](../_config.yml) for the project title, public URL,
repository and navigation. `url` is the origin; `baseurl` is the repository path,
or an empty string for a domain-root site. Navigation paths are relative to that
base URL. `hangry.background: none` disables the animated background; reduced
motion preferences also disable it.

The root README supplies the overview content, including release history. Keep
relative Markdown links usable on GitHub; the website resolves them to rendered
pages. Source-file links open on GitHub when the file is excluded from the site.
Use `<details markdown="1">` for collapsible sections containing Markdown, so
commands and tables render correctly in both Jekyll and GitHub.

## Reusing the theme

[`theme/`](theme/) is a self-contained Apache-2.0 Jekyll theme package, containing
the layout, brand asset, CSS, JavaScript, license and gemspec. It has no
project-specific paths or product text. This repository points `layouts_dir` and
`hangry.asset_root` at that local package, so deployment works without a separate
theme repository.

To share it across projects, publish the contents of `theme/` as a theme
repository or gem. A consumer can then use a pinned `remote_theme` reference or
install the gem, remove the local `layouts_dir` override, and use
`hangry.asset_root: /assets/hangry-pages`. Keep the README rendering plugins and
project-specific navigation settings in each consuming repository. The remote
theme should be published before consumers switch to it.

The gallery is independent of the theme, so it remains usable from Pages,
the Studio container, or a downloaded copy.
