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
| `category`    | list of strings | yes      | One or more categories that describe the plugin. See [Categories](#categories) below. |

### Categories

Use one or more of the following standard categories for `category`. If your plugin doesn't fit, open an issue to propose a new one rather than inventing one ad hoc:

- `PerceptionStrategy` — sensing, detection, tracking, segmentation, fusion
- `LocalizationStrategy` — pose estimation, SLAM-based localization
- `MappingStrategy` — map building, SLAM mapping, environment representation
- `PlanningStrategy` — global/local planners, behavior planning, decision-making
- `ControlStrategy` — vehicle controllers, actuation
- `Executer` — runtime execution, scheduling, orchestration
- `WorldBridge` — bridges to simulators, middleware, or external world interfaces

### Example Entry

```yaml
plugins:
  - name: my_perception_plugin
    description: One-line summary of what the plugin does
    repository: https://github.com/your-org/your-plugin-repo
    version: latest
    author: your-org
    category:
      - PerceptionStrategy
```

The authoritative list of registered plugins lives in [`plugins.yaml`](plugins.yaml). Tools and the AVLite runtime consume that file directly.

## Contributing

To add or update a plugin in this registry:

1. **Fork** this repository and create a feature branch.
2. **Edit `plugins.yaml`** and append (or update) your plugin entry following the [schema](#plugin-registry-schema) above. Keep entries alphabetically sorted by `name` to minimize merge conflicts.
3. **Verify your plugin repository** is public, has a clear `README`, a valid `LICENSE`, and a tagged release matching the `version` you list (unless you intentionally use `latest`).
4. **Open a pull request** with a short description of the plugin and a link to its repository. A maintainer will review and merge.

### Guidelines

- Only list plugins you maintain or have permission to register.
- Plugins must be open source under an OSI-approved license.
- Keep `description` short (under ~100 characters); put longer documentation in the plugin's own repository.
- Pin `version` to a specific tag for stability; reserve `latest` for actively developed plugins.

### Removing or Renaming a Plugin

If a plugin is no longer maintained or is being renamed, open a PR that updates or removes the corresponding entry in `plugins.yaml`, and explain the reason in the PR description.

## License

This registry is distributed under the terms of the [LICENSE](LICENSE) file in this repository. Each listed plugin is governed by the license of its own repository.