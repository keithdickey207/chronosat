extends Node3D
## Reads Chronosat JSON export and renders satellites around Earth.
## Demo-safe: output only, no source architecture exposure.

const DEFAULT_JSON := "res://../../output/orbital_positions.json"
const SCALE := 1.0 / 1_000_000.0  # meters → scene units (1 unit = 1000 km)
const EARTH_RADIUS_KM := 6378.137

@export var json_path: String = DEFAULT_JSON
@export var refresh_interval_s: float = 2.0
@export var auto_refresh: bool = true

var _satellite_nodes: Dictionary = {}
var _label_root: Node3D
var _camera: Camera3D
var _orbit_angle := 0.0

@onready var hud: Label = $CanvasLayer/HUD
@onready var status: Label = $CanvasLayer/Status


func _ready() -> void:
	_label_root = Node3D.new()
	_label_root.name = "Labels"
	add_child(_label_root)

	_camera = $Camera3D
	_build_earth()
	_load_and_render()

	if auto_refresh:
		var timer := Timer.new()
		timer.wait_time = refresh_interval_s
		timer.autostart = true
		timer.timeout.connect(_load_and_render)
		add_child(timer)


func _build_earth() -> void:
	var earth := MeshInstance3D.new()
	earth.name = "Earth"
	var sphere := SphereMesh.new()
	sphere.radius = EARTH_RADIUS_KM * SCALE
	sphere.height = sphere.radius * 2.0
	sphere.radial_segments = 48
	sphere.rings = 24
	earth.mesh = sphere

	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.12, 0.35, 0.62)
	mat.roughness = 0.85
	mat.metallic = 0.05
	earth.material_override = mat
	add_child(earth)

	# Subtle equator ring for orientation
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = EARTH_RADIUS_KM * SCALE * 0.998
	torus.outer_radius = EARTH_RADIUS_KM * SCALE * 1.002
	ring.mesh = torus
	var ring_mat := StandardMaterial3D.new()
	ring_mat.albedo_color = Color(0.3, 0.7, 1.0, 0.35)
	ring_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	ring.material_override = ring_mat
	add_child(ring)


func _load_and_render() -> void:
	var resolved := _resolve_json_path(json_path)
	if resolved.is_empty():
		status.text = "JSON not found: %s" % json_path
		return

	var text := FileAccess.get_file_as_string(resolved)
	if text.is_empty():
		status.text = "Empty or unreadable: %s" % resolved
		return

	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		status.text = "Invalid JSON schema"
		return

	_render_satellites(data)
	_update_hud(data)
	status.text = "Live — %s" % resolved.get_file()


func _resolve_json_path(path: String) -> String:
	if path.begins_with("res://"):
		var global := ProjectSettings.globalize_path(path)
		if FileAccess.file_exists(global):
			return global
		# Fallback: sibling output folder when running from editor
		var fallback := ProjectSettings.globalize_path("res://../../output/orbital_positions.json")
		if FileAccess.file_exists(fallback):
			return fallback
		return ""

	if FileAccess.file_exists(path):
		return path
	return ""


func _render_satellites(data: Dictionary) -> void:
	var sats: Array = data.get("satellites", [])
	var seen: Dictionary = {}

	for sat in sats:
		if typeof(sat) != TYPE_DICTIONARY:
			continue
		var norad: int = int(sat.get("norad_id", 0))
		var eci: Dictionary = sat.get("eci_km", {})
		var pos := Vector3(
			float(eci.get("x", 0.0)) * SCALE,
			float(eci.get("z", 0.0)) * SCALE,  # ECI Z → Godot Y (up)
			float(eci.get("y", 0.0)) * SCALE   # ECI Y → Godot Z
		)

		var node: MeshInstance3D
		if _satellite_nodes.has(norad):
			node = _satellite_nodes[norad]
		else:
			node = _make_satellite_node(sat)
			_satellite_nodes[norad] = node
			add_child(node)

		node.position = pos
		seen[norad] = true

	# Remove stale nodes
	for norad in _satellite_nodes.keys():
		if not seen.has(norad):
			_satellite_nodes[norad].queue_free()
			_satellite_nodes.erase(norad)


func _make_satellite_node(sat: Dictionary) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	node.name = "SAT_%d" % int(sat.get("norad_id", 0))

	var mesh := SphereMesh.new()
	mesh.radius = 0.025
	mesh.height = 0.05
	node.mesh = mesh

	var mat := StandardMaterial3D.new()
	var constellation: String = str(sat.get("constellation", "unknown"))
	mat.albedo_color = _color_for_constellation(constellation)
	mat.emission_enabled = true
	mat.emission = mat.albedo_color * 0.6
	node.material_override = mat

	return node


func _color_for_constellation(constellation: String) -> Color:
	match constellation:
		"crewed":
			return Color(1.0, 0.85, 0.2)
		"starlink":
			return Color(0.4, 0.75, 1.0)
		"navigation":
			return Color(0.3, 1.0, 0.5)
		"geostationary":
			return Color(1.0, 0.45, 0.3)
		"weather", "earth_obs":
			return Color(0.85, 0.5, 1.0)
		_:
			return Color(0.9, 0.9, 0.9)


func _update_hud(data: Dictionary) -> void:
	var count: int = int(data.get("satellite_count", 0))
	var ts: String = str(data.get("generated_at", "—"))
	hud.text = "CHRONOSAT v0.1  |  %d satellites  |  %s" % [count, ts]


func _process(delta: float) -> void:
	if _camera == null:
		return
	_orbit_angle += delta * 0.08
	var r := 18.0
	_camera.position = Vector3(
		sin(_orbit_angle) * r,
		6.0,
		cos(_orbit_angle) * r
	)
	_camera.look_at(Vector3.ZERO, Vector3.UP)
