"""
Prepara as mídias do site a partir dos originais do Instagram em _raw/media.

  python tools/media.py

Gera em dist/assets:
  video/hero-1.mp4, hero-2.mp4, hero-3.mp4  colunas do hero (mudas, 7 s)
  video/hero-m.mp4                         montagem vertical para celular
  video/p/{id}.mp4                         prévia muda de 6 s (vitrine)
  video/full/{id}.mp4                      reel completo com som (modal), até 60 s
  img/reels/{id}.jpg                       capa de cada reel
  img/fotos/{id}.jpg                       fotos
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "_raw" / "media"
OUT = ROOT / "dist" / "assets"
FF = str((ROOT.parent / "achilles-video" / "node_modules" / "ffmpeg-static" / "ffmpeg.exe").resolve())

# id: (início da prévia, segundo da capa)
REELS = {
    "DRAGuUTEaDq": (0.5, 1.0), "DgFpSydRGS1": (1.0, 1.5), "DZTdQFIxwIM": (0.5, 1.0),
    "DbD1sTBREH9": (0.5, 1.0), "DZQ0ZY8RGX2": (38, 42), "Ddy2d60xR--": (0.5, 3.0),
    "DfA8cQ1xklB": (0.5, 1.5), "DYqJ_SbRAyL": (2, 3), "DbPRBoex4lv": (1, 2),
    "DPcY-NWEZUs": (3, 4), "DXCQ4n7EQWF": (1, 1.5), "DaY5BBPR1TU": (1, 2),
    "Da_ZpN-xPr0": (1, 2), "DawPBh6x2nB": (1, 1.5), "DQ_1IvWkb91": (0.5, 1),
    "DQSfiHMETuE": (0.5, 1), "DddxVPjxCl7": (30, 36), "DfSzBPEhOKa": (2, 4),
    "DfP4oA9OV4J": (1, 8), "DXu877bkamW": (12, 22), "DO9BHLwkZOk": (1, 2),
}
FOTOS = ["DaxdsmokTvR-0", "DaxdsmokTvR-1", "DaxdsmokTvR-3", "DaxdsmokTvR-4", "DaxdsmokTvR-5",
         "DbV0Rt1RpBe-0", "DNddpBntWEs-0", "DNeeLmsNBYN-0", "DNJrU2MtIvJ-0", "DRDVdWYkf7f-0",
         "DQWxM3sETLo-0", "DRuCZwgkcdU-0", "DSqK8_6kXuD-0", "DYLFGuIkSIm-0", "DMh0I4vuSHj-0"]
# quadros parados tirados dos reels (nome: (id, segundo))
STILLS = {
    "cris-batom": ("DZQ0ZY8RGX2", 46), "cris-make": ("DfP4oA9OV4J", 6), "cris-fala": ("DfSzBPEhOKa", 4),
    "caza-espelho": ("DgFpSydRGS1", 8), "caza-sala": ("DRAGuUTEaDq", 13), "caza-rosa": ("DgFpSydRGS1", 1.5),
}
HERO = [("DgFpSydRGS1", 1.0), ("DRAGuUTEaDq", 0.3), ("DZTdQFIxwIM", 0.4)]
HERO_M = [("DZTdQFIxwIM", 0.4), ("DRAGuUTEaDq", 0.3), ("DbD1sTBREH9", 0.5), ("DgFpSydRGS1", 1.0), ("DfA8cQ1xklB", 0.5)]

V916 = "scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"


def run(args):
    r = subprocess.run([FF, "-loglevel", "error", "-y", *args])
    if r.returncode:
        sys.exit("ffmpeg falhou: " + " ".join(args))


def need(p):
    p.parent.mkdir(parents=True, exist_ok=True)
    return not p.exists() or "--force" in sys.argv


def main():
    for i, (rid, ss) in enumerate(HERO, 1):
        p = OUT / "video" / f"hero-{i}.mp4"
        if need(p):
            run(["-ss", str(ss), "-t", "7", "-i", str(RAW / f"{rid}.mp4"), "-an", "-vf", V916.format(w=540, h=960) + ",fps=30",
                 "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(p)])
            run(["-ss", "0.2", "-i", str(p), "-frames:v", "1", "-q:v", "4", str(p.with_suffix(".jpg"))])
        print("ok", p.name)

    p = OUT / "video" / "hero-m.mp4"
    if need(p):
        ins, parts = [], []
        for k, (rid, ss) in enumerate(HERO_M):
            ins += ["-ss", str(ss), "-t", "2.6", "-i", str(RAW / f"{rid}.mp4")]
            parts.append(f"[{k}:v]{V916.format(w=720, h=1280)},fps=30,trim=duration=2.6,setpts=PTS-STARTPTS[v{k}]")
        flt = ";".join(parts) + ";" + "".join(f"[v{k}]" for k in range(len(HERO_M))) + f"concat=n={len(HERO_M)}:v=1:a=0[o]"
        run([*ins, "-filter_complex", flt, "-map", "[o]", "-an", "-c:v", "libx264", "-crf", "28", "-preset", "slow",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(p)])
        run(["-ss", "0.2", "-i", str(p), "-frames:v", "1", "-q:v", "4", str(p.with_suffix(".jpg"))])
    print("ok", p.name)

    for rid, (ss, cover) in REELS.items():
        src = str(RAW / f"{rid}.mp4")
        prev = OUT / "video" / "p" / f"{rid}.mp4"
        if need(prev):
            run(["-ss", str(ss), "-t", "6", "-i", src, "-an", "-vf", V916.format(w=360, h=640) + ",fps=30",
                 "-c:v", "libx264", "-crf", "29", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(prev)])
        full = OUT / "video" / "full" / f"{rid}.mp4"
        if need(full):
            run(["-i", src, "-t", "60", "-vf", V916.format(w=540, h=960), "-c:v", "libx264", "-crf", "28", "-preset", "slow",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(full)])
        jpg = OUT / "img" / "reels" / f"{rid}.jpg"
        if need(jpg):
            run(["-ss", str(cover), "-i", src, "-frames:v", "1", "-vf", V916.format(w=720, h=1280), "-q:v", "4", str(jpg)])
        print("ok", rid)

    for name, (rid, t) in STILLS.items():
        jpg = OUT / "img" / "stills" / f"{name}.jpg"
        if need(jpg):
            run(["-ss", str(t), "-i", str(RAW / f"{rid}.mp4"), "-frames:v", "1", "-q:v", "3", str(jpg)])
        print("ok", name)

    for fid in FOTOS:
        jpg = OUT / "img" / "fotos" / f"{fid}.jpg"
        if need(jpg):
            run(["-i", str(RAW / f"{fid}.jpg"), "-vf", "scale='min(1200,iw)':-2", "-q:v", "4", str(jpg)])
        print("ok", fid)


if __name__ == "__main__":
    main()
