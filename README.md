# avlite-community-plugins

A central registry of community-maintained plugins for [AVLite](https://github.com/AV-Lab). This repository does **not** host plugin source code — each entry in the registry points to an external GitHub repository where the plugin lives. Tools and the AVLite runtime can consume `plugins.yaml` to discover, fetch, and install plugins.

## Plugin Registry Schema

`plugins.yaml` has a single top-level key, `plugins`, whose value is a list of plugin entries. Each entry uses the following fields:

| Field                 | Type            | Required | Description |
| --------------------- | --------------- | :------: | ----------- |
| `name`                | string          | yes      | Unique plugin identifier. Official AV-Lab plugins use `avlite-*` kebab-case (e.g. `avlite-bridge-carla`). Community plugins may use `snake_case`. Must be unique within `plugins.yaml`. |
| `description`         | string          | yes      | One-line summary of what the plugin does. |
| `repository`          | URL (string)    | yes      | Public Git URL where the plugin source lives (typically a GitHub repository). |
| `version`             | string          | yes      | Plugin version. Use a semver tag (e.g. `1.2.0`) or `latest` to track the default branch. |
| `author`              | string          | yes      | Author name, GitHub user, or organization that maintains the plugin. |
| `category`            | list of strings | yes      | One or more categories that describe the plugin. See [Categories](#categories) below. |
| `min_avlite_version`  | string          | no       | Minimum AVLite version required (semver, e.g. `0.4.5`). Omit or leave empty if unknown. |
| `dependency_notes`    | string          | no       | Extra setup beyond the plugin's `requirements.txt` (system packages, ROS, simulators, etc.). Use `""` when pip-only. |

### Categories

Use one or more of the following standard categories for `category`. If your plugin doesn't fit, open an issue to propose a new one rather than inventing one ad hoc:

- `PerceptionStrategy` — monolithic perception (detect + track + predict in one class)
- `DetectionStrategy` — PerceptionPipeline detect stage
- `TrackingStrategy` — PerceptionPipeline track stage
- `PredictionStrategy` — PerceptionPipeline predict stage
- `LocalizationStrategy` — pose estimation, SLAM-based localization
- `MappingStrategy` — map building, SLAM mapping, environment representation
- `GlobalPlannerStrategy` — global planners
- `LocalPlanningStrategy` — local planners (including behavioral, path, velocity, and lattice stages)
- `ControlStrategy` — vehicle controllers, actuation
- `ExecutionStrategy` — runtime executers, scheduling, orchestration
- `TaskStrategy` — stack-extension execution tasks (every cycle / interval / ON_EVENT)
- `WorldBridge` — bridges to simulators, middleware, or external world interfaces
- `AppStrategy` — CLI/GUI app entry plugins

### Example entries

**Official AV-Lab plugin (kebab-case):**

```yaml
plugins:
  - name: avlite-bridge-carla
    description: CARLA simulator world bridge for AVLite
    repository: https://github.com/AV-Lab/avlite-bridge-carla
    version: latest
    author: AV-Lab
    category:
      - WorldBridge
    min_avlite_version: "0.4.5"
    dependency_notes: "Running CARLA server required; start CARLA before AVLite."
```

**Community plugin (snake_case):**

```yaml
plugins:
  - name: my_perception_plugin
    description: One-line summary of what the plugin does
    repository: https://github.com/your-org/your-plugin-repo
    version: latest
    author: your-org
    category:
      - PerceptionStrategy
    min_avlite_version: "0.4.5"
    dependency_notes: ""
```

### Registered official plugins

| Name | Repository |
|------|------------|
| `avlite-bridge-carla` | [AV-Lab/avlite-bridge-carla](https://github.com/AV-Lab/avlite-bridge-carla) |
| `avlite-bridge-gazebo` | [AV-Lab/avlite-bridge-gazebo](https://github.com/AV-Lab/avlite-bridge-gazebo) |
| `avlite-bridge-ROS2` | [AV-Lab/avlite-bridge-ROS2](https://github.com/AV-Lab/avlite-bridge-ROS2) |
| `avlite-controller-joystick` | [AV-Lab/avlite-controller-joystick](https://github.com/AV-Lab/avlite-controller-joystick) |
| `avlite-executer-ROS2` | [AV-Lab/avlite-executer-ROS2](https://github.com/AV-Lab/avlite-executer-ROS2) |

See [`plugins.yaml`](plugins.yaml) for the full list (including community samples).

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
- Prefer setting `min_avlite_version` when you know the floor; use `dependency_notes` for anything users must install or source beyond `requirements.txt`.

### Removing or Renaming a Plugin

If a plugin is no longer maintained or is being renamed, open a PR that updates or removes the corresponding entry in `plugins.yaml`, and explain the reason in the PR description.

## License

This registry is distributed under the terms of the [LICENSE](LICENSE) file in this repository. Each listed plugin is governed by the license of its own repository.
