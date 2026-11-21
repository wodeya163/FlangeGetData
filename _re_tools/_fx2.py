import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("def recommend_oring(d_shaft, seal_type, medium, rod_mode):",
              "def recommend_oring(d_shaft, seal_type, medium=None, rod_mode=False):")
s = s.replace("def calc_groove(d2, seal_type, with_backup, double_backup, pressure_dir, pressure):",
              "def calc_groove(d2, seal_type='static_radial', with_backup=False,\n                double_backup=False, pressure_dir=None, pressure=None):")
s = s.replace("def get_compression_check(d2, h, seal_type):",
              "def get_compression_check(d2, h, seal_type='static_radial'):")
s = s.replace("def recommend_material(medium, temp_min, temp_max):",
              "def recommend_material(medium=None, temp_min=None, temp_max=None):")
s = s.replace("def recommend_material_ex(medium, temp_min, temp_max):",
              "def recommend_material_ex(medium=None, temp_min=None, temp_max=None):")
s = s.replace("def assess_backup_ring(pressure_mpa, gap_mm, hardness, temp_max):",
              "def assess_backup_ring(pressure_mpa=None, gap_mm=None, hardness=None, temp_max=None):")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
