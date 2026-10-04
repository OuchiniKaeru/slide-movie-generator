import argparse
import json
import sys
from typing import Any

from tools.audio.editor import concat_audio, cut_audio, denoise_audio, normalize_audio
from tools.audio.filler import detect_filler
from tools.audio.info import get_audio_info
from tools.audio.noise import detect_noise
from tools.audio.renderer import render_audio_from_plan
from tools.audio.silence import detect_silence
from tools.audio.transcribe import transcribe_audio
from tools.asset.asset_tools import asset_convert, asset_generate, asset_resize, asset_search
from tools.scene.scene_tools import scene_create, scene_delete, scene_read, scene_update
from tools.animation.animation_tools import animation_add, animation_delete, animation_update
from tools.video.video_tools import render_preview, render_scene, render_video, video_extract_frame, video_inspect
from tools.subtitle.subtitle_tools import generate_subtitles
from tools.project.project_tools import project_init, project_status, project_update_stage


def print_json(obj: Any):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Video Production Agent CLI Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Audio Tools
    p_info = subparsers.add_parser("audio_get_info")
    p_info.add_argument("audio_path")

    p_trans = subparsers.add_parser("audio_transcribe")
    p_trans.add_argument("audio_path")
    p_trans.add_argument("--output", "-o", default=None)
    p_trans.add_argument("--language", default="ja")
    p_trans.add_argument("--model", default="base")

    p_silence = subparsers.add_parser("audio_detect_silence")
    p_silence.add_argument("audio_path")
    p_silence.add_argument("--min-duration", type=float, default=0.8)
    p_silence.add_argument("--threshold-db", type=float, default=-40.0)
    p_silence.add_argument("--output", "-o", default=None)

    p_filler = subparsers.add_parser("audio_detect_filler")
    p_filler.add_argument("transcript_path")
    p_filler.add_argument("--output", "-o", default=None)

    p_noise = subparsers.add_parser("audio_detect_noise")
    p_noise.add_argument("audio_path")
    p_noise.add_argument("--output", "-o", default=None)

    p_cut = subparsers.add_parser("audio_cut")
    p_cut.add_argument("input_path")
    p_cut.add_argument("output_path")
    p_cut.add_argument("--start", type=float, required=True)
    p_cut.add_argument("--end", type=float, default=None)

    p_concat = subparsers.add_parser("audio_concat")
    p_concat.add_argument("output_path")
    p_concat.add_argument("inputs", nargs="+")
    p_concat.add_argument("--crossfade", type=int, default=50)

    p_norm = subparsers.add_parser("audio_normalize")
    p_norm.add_argument("input_path")
    p_norm.add_argument("output_path")
    p_norm.add_argument("--target-db", type=float, default=-1.0)

    p_denoise = subparsers.add_parser("audio_denoise")
    p_denoise.add_argument("input_path")
    p_denoise.add_argument("output_path")

    p_render_audio = subparsers.add_parser("audio_render")
    p_render_audio.add_argument("original_audio")
    p_render_audio.add_argument("edit_plan")
    p_render_audio.add_argument("output_audio")
    p_render_audio.add_argument("--crossfade", type=int, default=40)

    # Asset Tools
    p_asearch = subparsers.add_parser("asset_search")
    p_asearch.add_argument("project_dir")
    p_asearch.add_argument("--query", "-q", default="")
    p_asearch.add_argument("--category", "-c", default=None)

    p_agenerate = subparsers.add_parser("asset_generate")
    p_agenerate.add_argument("project_dir")
    p_agenerate.add_argument("asset_id")
    p_agenerate.add_argument("--type", default="diagram")
    p_agenerate.add_argument("--text", default="")
    p_agenerate.add_argument("--width", type=int, default=1920)
    p_agenerate.add_argument("--height", type=int, default=1080)

    p_aresize = subparsers.add_parser("asset_resize")
    p_aresize.add_argument("input_path")
    p_aresize.add_argument("output_path")
    p_aresize.add_argument("--width", type=int, default=None)
    p_aresize.add_argument("--height", type=int, default=None)

    p_aconvert = subparsers.add_parser("asset_convert")
    p_aconvert.add_argument("input_path")
    p_aconvert.add_argument("output_path")
    p_aconvert.add_argument("--format", default="PNG")

    # Scene Tools
    p_screate = subparsers.add_parser("scene_create")
    p_screate.add_argument("project_dir")
    p_screate.add_argument("scene_id")
    p_screate.add_argument("--duration", type=float, default=5.0)

    p_sread = subparsers.add_parser("scene_read")
    p_sread.add_argument("project_dir")
    p_sread.add_argument("scene_id")

    p_sdelete = subparsers.add_parser("scene_delete")
    p_sdelete.add_argument("project_dir")
    p_sdelete.add_argument("scene_id")

    # Animation Tools
    p_aanim = subparsers.add_parser("animation_add")
    p_aanim.add_argument("project_dir")
    p_aanim.add_argument("scene_id")
    p_aanim.add_argument("element_id")
    p_aanim.add_argument("anim_type")
    p_aanim.add_argument("--start", type=float, required=True)
    p_aanim.add_argument("--duration", type=float, required=True)
    p_aanim.add_argument("--easing", default="ease_out")

    # Video Tools
    p_rscene = subparsers.add_parser("render_scene")
    p_rscene.add_argument("project_dir")
    p_rscene.add_argument("scene_id")
    p_rscene.add_argument("--output", "-o", default=None)

    p_rpreview = subparsers.add_parser("render_preview")
    p_rpreview.add_argument("project_dir")
    p_rpreview.add_argument("--output", "-o", default=None)

    p_rvideo = subparsers.add_parser("render_video")
    p_rvideo.add_argument("project_dir")
    p_rvideo.add_argument("--output", "-o", default=None)

    p_vinspect = subparsers.add_parser("video_inspect")
    p_vinspect.add_argument("video_path")

    p_vextract = subparsers.add_parser("video_extract_frame")
    p_vextract.add_argument("video_path")
    p_vextract.add_argument("time_offset", type=float)
    p_vextract.add_argument("output_image")

    # Subtitle Tools
    p_sub = subparsers.add_parser("subtitle_generate")
    p_sub.add_argument("transcript_path")
    p_sub.add_argument("output_dir")

    # Project Tools
    p_pinit = subparsers.add_parser("project_init")
    p_pinit.add_argument("project_dir")
    p_pinit.add_argument("--project-id", default=None)
    p_pinit.add_argument("--audio", default=None)

    p_pstatus = subparsers.add_parser("project_status")
    p_pstatus.add_argument("project_dir")

    p_pstage = subparsers.add_parser("project_stage")
    p_pstage.add_argument("project_dir")
    p_pstage.add_argument("stage")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd = args.command

    # Dispatch commands
    if cmd == "audio_get_info":
        print_json(get_audio_info(args.audio_path))
    elif cmd == "audio_transcribe":
        print_json(transcribe_audio(args.audio_path, args.output, args.language, args.model))
    elif cmd == "audio_detect_silence":
        print_json(detect_silence(args.audio_path, args.min_duration, args.threshold_db, args.output))
    elif cmd == "audio_detect_filler":
        print_json(detect_filler(transcript_path=args.transcript_path, output_path=args.output))
    elif cmd == "audio_detect_noise":
        print_json(detect_noise(args.audio_path, output_path=args.output))
    elif cmd == "audio_cut":
        res = cut_audio(args.input_path, args.output_path, args.start, args.end)
        print_json({"status": "success", "output_path": res})
    elif cmd == "audio_concat":
        res = concat_audio(args.inputs, args.output_path, args.crossfade)
        print_json({"status": "success", "output_path": res})
    elif cmd == "audio_normalize":
        res = normalize_audio(args.input_path, args.output_path, args.target_db)
        print_json({"status": "success", "output_path": res})
    elif cmd == "audio_denoise":
        res = denoise_audio(args.input_path, args.output_path)
        print_json({"status": "success", "output_path": res})
    elif cmd == "audio_render":
        print_json(render_audio_from_plan(args.original_audio, args.edit_plan, args.output_audio, args.crossfade))
    elif cmd == "asset_search":
        print_json(asset_search(args.project_dir, args.query, args.category))
    elif cmd == "asset_generate":
        print_json(asset_generate(args.project_dir, args.asset_id, args.type, args.text, args.width, args.height))
    elif cmd == "asset_resize":
        print_json(asset_resize(args.input_path, args.output_path, args.width, args.height))
    elif cmd == "asset_convert":
        print_json(asset_convert(args.input_path, args.output_path, args.format))
    elif cmd == "scene_create":
        print_json(scene_create(args.project_dir, args.scene_id, args.duration))
    elif cmd == "scene_read":
        print_json(scene_read(args.project_dir, args.scene_id))
    elif cmd == "scene_delete":
        print_json(scene_delete(args.project_dir, args.scene_id))
    elif cmd == "animation_add":
        print_json(animation_add(args.project_dir, args.scene_id, args.element_id, args.anim_type, args.start, args.duration, args.easing))
    elif cmd == "render_scene":
        print_json(render_scene(args.project_dir, args.scene_id, args.output))
    elif cmd == "render_preview":
        print_json(render_preview(args.project_dir, args.output))
    elif cmd == "render_video":
        print_json(render_video(args.project_dir, args.output))
    elif cmd == "video_inspect":
        print_json(video_inspect(args.video_path))
    elif cmd == "video_extract_frame":
        print_json(video_extract_frame(args.video_path, args.time_offset, args.output_image))
    elif cmd == "subtitle_generate":
        print_json(generate_subtitles(args.transcript_path, args.output_dir))
    elif cmd == "project_init":
        print_json(project_init(args.project_dir, args.project_id, args.audio))
    elif cmd == "project_status":
        print_json(project_status(args.project_dir))
    elif cmd == "project_stage":
        print_json(project_update_stage(args.project_dir, args.stage))


if __name__ == "__main__":
    main()
