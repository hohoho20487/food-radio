import requests
import wave
import io
import os
import re
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VOICEVOX_URL = "http://localhost:50021"

# VOICEVOXのインストール候補パス（自動起動用）
VOICEVOX_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\VOICEVOX\VOICEVOX.exe"),
    r"C:\Program Files\VOICEVOX\VOICEVOX.exe",
    r"C:\Program Files (x86)\VOICEVOX\VOICEVOX.exe",
]

SPEAKERS = {
    "リク": 82,  # 青山龍星（不機嫌）
    "サキ": 65,  # 波音リツ（クイーン）
    "ケン": 12,  # 白上虎太郎（ふつう）
    "ハナ": 65,  # 波音リツ（クイーン）
}

CREDIT_LINES = {
    "リク": ("リク", "VOICEVOX：青山龍星"),
    "サキ": ("サキ", "VOICEVOX：波音リツ"),
    "ケン": ("ケン", "VOICEVOX：白上虎太郎"),
    "ハナ": ("ハナ", "VOICEVOX：波音リツ"),
}


def voicevox_is_up() -> bool:
    try:
        requests.get(f"{VOICEVOX_URL}/version", timeout=2)
        return True
    except requests.RequestException:
        return False


def ensure_voicevox(wait_sec: int = 60) -> None:
    """VOICEVOXが起動していなければ自動起動を試み、APIが応答するまで待つ。"""
    if voicevox_is_up():
        return

    exe = next((p for p in VOICEVOX_PATHS if Path(p).exists()), None)
    if exe is None:
        print("VOICEVOXが見つかりません。手動で起動してください。")
        print("候補パス: " + " / ".join(VOICEVOX_PATHS))
        sys.exit(1)

    print(f"VOICEVOXを起動中... ({exe})")
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([exe], creationflags=creationflags, close_fds=True)

    deadline = time.time() + wait_sec
    while time.time() < deadline:
        if voicevox_is_up():
            print("VOICEVOX起動完了\n")
            return
        time.sleep(2)

    print(f"VOICEVOXの起動を{wait_sec}秒待ちましたがAPIに接続できませんでした。")
    sys.exit(1)


def get_audio(text: str, speaker_id: int) -> bytes:
    query = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
    )
    query.raise_for_status()

    synthesis = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker_id},
        json=query.json(),
    )
    synthesis.raise_for_status()
    return synthesis.content


def parse_script(md_path: Path) -> list[tuple[str, str]]:
    dialogues = []
    pattern = re.compile(r"^(リク|サキ|ケン|ハナ)：「(.+?)」\s*$")
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                dialogues.append((m.group(1), m.group(2)))
    return dialogues


def make_silence(params: wave._wave_params, duration_sec: float) -> bytes:
    n_frames = int(params.framerate * duration_sec)
    output = io.BytesIO()
    with wave.open(output, "wb") as w:
        w.setparams(params)
        w.writeframes(b"\x00" * n_frames * params.sampwidth * params.nchannels)
    return output.getvalue()


def merge_wav(wav_bytes_list: list[bytes]) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as out_wav:
        for i, wav_bytes in enumerate(wav_bytes_list):
            with wave.open(io.BytesIO(wav_bytes), "rb") as in_wav:
                if i == 0:
                    out_wav.setparams(in_wav.getparams())
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
    return output.getvalue()


def main():
    if len(sys.argv) < 2:
        print("使い方: python tts.py <台本.md>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"ファイルが見つかりません: {md_path}")
        sys.exit(1)

    ensure_voicevox()

    print(f"台本読み込み: {md_path.name}")
    dialogues = parse_script(md_path)
    if not dialogues:
        print("セリフが見つかりませんでした。")
        sys.exit(1)

    print(f"{len(dialogues)}行のセリフを検出\n")

    wav_list = []
    seen_characters = []
    for i, (character, text) in enumerate(dialogues, 1):
        preview = text[:20] + ("..." if len(text) > 20 else "")
        print(f"[{i}/{len(dialogues)}] {character}：{preview}")
        wav_list.append(get_audio(text, SPEAKERS[character]))
        if character not in seen_characters:
            seen_characters.append(character)

    print("\nクレジット音声を生成中...")
    credits = [CREDIT_LINES[c] for c in seen_characters if c in CREDIT_LINES]
    credit_wavs = []
    for character, text in credits:
        print(f"  {character}：{text}")
        credit_wavs.append(get_audio(text, SPEAKERS[character]))

    main_wav = merge_wav(wav_list)
    with wave.open(io.BytesIO(main_wav), "rb") as w:
        params = w.getparams()
    silence = make_silence(params, 1.0)

    output_path = md_path.with_suffix(".wav")
    output_path.write_bytes(merge_wav([main_wav, silence] + credit_wavs))
    print(f"\n完了 → {output_path}")


if __name__ == "__main__":
    main()
