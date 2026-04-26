import subprocess


def check_lean_file(path: str):
    try:
        result = subprocess.run(
            ["lean", path],
            capture_output=True,
            text=True
        )

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "errors": result.stderr
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }