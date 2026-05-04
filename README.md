# avlite-community-plugins

A central registry of community-maintained plugins for [AVLite](https://github.com/AV-Lab). This repository does **not** host plugin source code — each entry in the registry points to an external GitHub repository where the plugin lives. Tools and the AVLite runtime can consume `plugins.yaml` to discover, fetch, and install plugins.

## Plugin Registry Schema

`plugins.yaml` has a single top-level key, `plugins`, whose value is a list of plugin entries. Each entry uses the following fields:

| Field         | Type            | Required | Description |
| ------------- | --------------- | :------: | ----------- |
| `name`        | string          | yes      | Unique plugin identifier. Use `snake_case` and avoid spaces. Must be unique within `plugins.yaml`. |
| `description` | string          | yes      | One-line summary of what the plugin does. |
| `repository`  | URL (string)    | yes      | Public Git URL where the plugin source lives (typically a GitHub repository). |
| `version`     | string          | yes      | Plugin version. Use a semver tag (e.g. `1.2.0`) or `latest` to track the default branch. |
| `author`      | string          | yes      | Author name, GitHub user, or organization that maintains the plugin. |
| `category`    | string          | yes      | Primary category. See [Categories](#categories) below. |
| `tags`        | list of strings | no       | Free-form tags used for search and filtering (e.g. `lidar`, `ros2`, `simulation`). |

### Categories

Use one of the following standard categories for `category`. If your plugin doesn't fit, open an issue to propose a new one rather than inventing one ad hoc:

- `perception` — sensing, detection, tracking, segmentation, fusion
- `planning` — global/local planners, behavior planning, decision-making
- `control` — vehicle controllers, actuation
- `localization` — mapping, SLAM, pose estimation
- `simulation` — simulators, scenario generation, synthetic data
- `visualization` — UIs, dashboards, debug tooling
- `utility` — shared libraries, helpers, integrations

### Example Entry

```yaml
plugins:
  - name: ORBit_perception
    description: ORBit perception plugin for AVLite
    repository: https://github.com/AV-Lab/ORBit_perception
    version: latest
    author: AV-Lab
    category: perception
    tags:
      - perception
      - computer-vision
```

## Available Plugins

| Name | Category | Description | Repository |
| ---- | -------- | ----------- | ---------- |
| ORBit_perception | perception | ORBit perception plugin for AVLite | https://github.com/AV-Lab/ORBit_perception |
| sample_avlite_plugin | perception | Sample AVLite plugin demonstrating the plugin interface | https://github.com/AV-Lab/sample-avlite-plugin |

## Contributing

To add or update a plugin in this registry:

1. **Fork** this repository and create a feature branch.
2. **Edit `plugins.yaml`** and append (or update) your plugin entry following the [schema](#plugin-registry-schema) above. Keep entries alphabetically sorted by `name` to minimize merge conflicts.
3. **Update the [Available Plugins](#available-plugins) table** in this README so the human-readable listing stays in sync with `plugins.yaml`.
4. **Verify your plugin repository** is public, has a clear `README`, a valid `LICENSE`, and a tagged release matching the `version` you list (unless you intentionally use `latest`).
5. **Open a pull request** with a short description of the plugin and a link to its repository. A maintainer will review and merge.

### Guidelines

- Only list plugins you maintain or have permission to register.
- Plugins must be open source under an OSI-approved license.
- Keep `description` short (under ~100 characters); put longer documentation in the plugin's own repository.
- Pin `version` to a specific tag for stability; reserve `latest` for actively developed plugins.

### Removing or Renaming a Plugin

If a plugin is no longer maintained or is being renamed, open a PR that updates or removes the corresponding entry in `plugins.yaml` and the [Available Plugins](#available-plugins) table, and explain the reason in the PR description.

## License

This registry is distributed under the terms of the [LICENSE](LICENSE) file in this repository. Each listed plugin is governed by the license of its own repository.