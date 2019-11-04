import subprocess as sp
import os
import re
from pkg_resources import parse_version


def run_cmd(cmd, shell=False):
    if isinstance(cmd, str):
        cmd = cmd.strip().split(" ")
    try:
        resp = sp.check_output(cmd, stderr=sp.STDOUT, shell=shell)
        return resp.decode()
    except sp.CalledProcessError as err:
        print("Called Process Error: %s" % err)
        print(err.output)
        return ""


def run_pdfgrep(file):
    try:
        cmd = ["pdfgrep", "-m", "1", "\\(3GPP TS", file]
        resp = sp.check_output(cmd, stderr=sp.STDOUT, shell=False)
        return resp.decode()
    except sp.CalledProcessError as err:
        if err.returncode == 1:
            return ""
        if err.output:
            print("CalledProcessError: %s" % err.output)
        else:
            print("CalledProcessError: %s" % err)
    return ""


def main(base_dir, sub_dir="etsi_ts"):
    cnt = 0
    latest_ts = {}
    pattern = re.compile("3GPP TS ([\d\.\-]+) version ([\d\.]+)( Release (\d+))?")

    # clean up old links and create new directory layout
    for cur_dir in [
        "etsi_ts_by_chapter",
        "etsi_ts_by_release_all",
        "etsi_ts_by_release_latest",
    ]:
        target_dir = os.path.join(base_dir, cur_dir)
        if os.path.exists(target_dir):
            import shutil

            shutil.rmtree(target_dir)
        os.mkdir(target_dir)

    for (path, dirs, files) in os.walk(os.path.join(base_dir, sub_dir)):
        for filename in files:
            if filename[-3:].lower() != "pdf":
                continue
            filepath = os.path.join(path, filename)

            # pdf needs to contain 3GPP Title
            res = run_pdfgrep(filepath).strip().strip("()").strip()
            if not res or res.strip() == "":
                continue

            # Extract TS, Version & Release
            match = pattern.match(res)
            if not match:
                continue
            ts, version, _, release = match.groups()
            print(filename, "-->", res)

            # create links
            if version:
                src_file = filepath.replace(base_dir, "..")
                target_dir = os.path.join(base_dir, "etsi_ts_by_chapter")
                target_file = os.path.join(target_dir, "TS%s-%s.pdf" % (ts, version))
                while os.path.exists(target_file):
                    target_file = os.path.join(
                        target_dir, "TS%s-%s-conflicted%d.pdf" % (ts, version, cnt),
                    )
                os.symlink(src_file, target_file)

            if version and release:
                release = int(release)
                src_file = filepath.replace(base_dir, "../..")
                target_dir = os.path.join(
                    base_dir, "etsi_ts_by_release_all/release_%02d" % (release)
                )
                target_file = os.path.join(target_dir, "TS%s-%s.pdf" % (ts, version))
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)
                while os.path.exists(target_file):
                    target_file = os.path.join(
                        target_dir, "TS%s-%s-conflicted%d.pdf" % (ts, version, cnt),
                    )
                os.symlink(src_file, target_file)

                # save latest ts
                other_ts = latest_ts.setdefault(release, {}).get(ts, None)
                if not other_ts or parse_version(other_ts["version"]) < parse_version(
                    version
                ):
                    latest_ts[release][ts] = {
                        "ts": ts,
                        "version": version,
                        "release": release,
                        "filepath": filepath,
                    }

            cnt += 1

    for release, release_ts in latest_ts.items():
        for ts, item in release_ts.items():
            src_file = item["filepath"].replace(base_dir, "../..")
            target_dir = os.path.join(
                base_dir, "etsi_ts_by_release_latest/release_%02d" % (release)
            )
            target_file = os.path.join(
                target_dir, "TS%s-%s.pdf" % (ts, item["version"])
            )
            if not os.path.exists(target_dir):
                os.mkdir(target_dir)
            while os.path.exists(target_file):
                target_file = os.path.join(
                    target_dir, "TS%s-%s.pdf" % (ts, item["version"])
                )
            os.symlink(src_file, target_file)


if __name__ == "__main__":
    main("./www.etsi.org/deliver")
