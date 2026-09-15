# avlite-community-plugins

A central registry of community-maintained plugins for [AVLite](https://github.com/AV-Lab). This repository does **not** host plugin source code — each entry in the registry points to an external GitHub repository where the plugin lives. Tools and the AVLite runtime can consume `plugins.yaml` to discover, fetch, and install plugins.

## Plugin Registry Schema

`plugins.yaml` has a single top-level key, `plugins`, whose value is a list of plugin entries. Each entry uses the following fields:

| Field                 | Type            | Required | Description |
| --------------------- | --------------- | :------: | ----------- |
| `name`                | string          | yes      | Unique plugin identifier, also used as the install folder name. Official AV-Lab plugins use `avlite-*` kebab-case (e.g. `avlite-bridge-carla`). Community plugins may use `snake_case`. Must be unique within `plugins.yaml`. |
| `display_name`        | string          | no       | Human-readable plugin name shown in the AVLite Plugins window and the plugin store (e.g. `AVLite CARLA Bridge`). Use spaces and normal capitalization; keep acronyms uppercase. Omit it to fall back to `name`. |
| `description`         | string          | yes      | One-line summary of what the plugin does. |
| `repository`          | URL (string)    | yes      | Public Git URL where the plugin source lives (typically a GitHub repository). |
| `version`             | string          | yes      | Plugin version. Use a semver tag (e.g. `1.2.0`) or `latest` to track the default branch. |
| `author`              | string          | yes      | Author name, GitHub user, or organization that maintains the plugin. |
| `category`            | list of strings | yes      | One or more categories that describe the plugin. See [Categories](#categories) below. |
| `min_avlite_version`  | string          | no       | Minimum AVLite version required (semver, e.g. `0.4.5`). Omit or leave empty if unknown. |
| `require_ros`         | bool            | no       | `true` if the plugin needs ROS 2 at runtime. Omit or `false` if it does not. |
| `min_ros_version`     | string          | no       | Oldest ROS 2 distro name this plugin supports (e.g. `humble`). Ignored unless `require_ros` is `true`. Omit for any installed ROS 2. |
| `max_ros_version`     | string          | no       | Newest ROS 2 distro name this plugin supports (e.g. `jazzy`). Omit for no upper bound. |
| `dependency_notes`    | string          | no       | Extra setup beyond the plugin's `requirements.txt` (system packages, ROS, simulators, etc.). Use `""` when pip-only. |
| `site_url`            | URL (string)    | no       | Project website or documentation page for the plugin (e.g. `https://example.org/my-plugin`). Omit or use `""` when the repository is the only home. |

### Categories

Use one or more of the following standard categories for `category`. If your plugin doesn't fit, open an issue to propose a new one rather than inventing one ad hoc:

- `PerceptionStrategy` — monolithic perception (detect + track + predict in one class)
- `DetectionStrategy` — PerceptionPipeline detect stage
- `TrackingStrategy` — PerceptionPipeline track stage
- `PredictionStrategy` — PerceptionPipeline predict stage; advertise exactly one typed forecast cap (`PREDICTION_TRAJECTORY`, `PREDICTION_GP`, `PREDICTION_GMM`, or `PREDICTION_OCCUPANCY`). There is no generic `PREDICTION`. Built-in lattice/velocity planners only soft-use `PREDICTION_TRAJECTORY` (`SingleTrajectory`).
- `LocalizationStrategy` — pose estimation, SLAM-based localization
- `MappingStrategy` — map building, SLAM mapping, environment representation; advertise `MAP_HD`, `MAP_RACE_TRACK`, and/or `MAP_OCCUPANCY` to match the map type you write.
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
    display_name: AVLite CARLA Bridge
    description: CARLA simulator world bridge for AVLite
    repository: https://github.com/AV-Lab/avlite-bridge-carla
    version: latest
    author: AV-Lab
    category:
      - WorldBridge
    min_avlite_version: "0.4.5"
    dependency_notes: "Running CARLA server required; start CARLA before AVLite."
    site_url: ""
```

**Community plugin (snake_case):**

```yaml
plugins:
  - name: my_perception_plugin
    display_name: My Perception Plugin
    description: One-line summary of what the plugin does
    repository: https://github.com/your-org/your-plugin-repo
    version: latest
    author: your-org
    category:
      - PerceptionStrategy
    min_avlite_version: "0.4.5"
    require_ros: false
    min_ros_version: ""
    max_ros_version: ""
    dependency_notes: ""
    site_url: "https://example.org/my-perception-plugin"
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
- Prefer setting `min_avlite_version` when you know the floor. Set `require_ros: true` and `min_ros_version` (optionally `max_ros_version`) when the plugin needs ROS 2. Use `dependency_notes` for anything else users must install or source beyond `requirements.txt`.
- WorldBridge plugins may include `launch.sh` at the repository root. AVLite warns and can run it in the background to start a vehicle platform or simulator (for example CARLA). The process keeps running after the stack stops.
- Plugins may include `<name>.yaml` at the repository root (registry `name`, e.g. `avlite-bridge-carla.yaml`; same format as `configs/<profile>.yaml`). After Install or Update, AVLite offers to add it as that profile. `c62_community_plugins` must list only this plugin — AVLite will not install other plugins automatically.
- `name` is an identifier, not a title: AVLite uses it for the install folder, the `avlite.plugins.<name>` import path, the plugin settings file, and profile entries, so it must stay free of spaces and must not change once published. Set `display_name` when the identifier reads poorly to users.
- Use `site_url` for a project website or documentation page — not a second copy of `repository`.

### Removing or Renaming a Plugin

If a plugin is no longer maintained or is being renamed, open a PR that updates or removes the corresponding entry in `plugins.yaml`, and explain the reason in the PR description.

## License

This registry is distributed under the terms of the [LICENSE](LICENSE) file in this repository. Each listed plugin is governed by the license of its own repository.
