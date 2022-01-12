import subprocess
import traceback


def subproc_error_wrapper(cmd):
    """
    This error handling function wraps around a subprocess.run
    call and provides more text output when the commands called return
    error. This function catches the subprocess.CalledProcessError
    often thrown and instead raises different errors based on the output.
    NOTE: subprocess.run sometimes thows different errors (like
    FileNotFoundError when the 1st arg is a command that cannot be found).

    Exceptions Raised:
    ==================
    * FileNotFoundError when cmd 1st arg cmd not found.
    * RuntimeError if output cannot otherwise be parsed.
    """

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            # shell=True
            # stdout=subprocess.DEVNULL,
            # # ^ Ignores stdout
            # stderr=subprocess.PIPE
            # # ^ Captures stderr so e.stderr is populated if needed
        )
    except(subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(strfy_subproc_error(e, cmd))


def strfy_subproc_error(e, cmd=[]):
    """
    Generates a string with lots of info to help debug a subproc gone wrong.
    Likely copy-pasted from https://github.com/7yl4r/subproc-test .

    params:
    -------
    e : Exception
        the exception thrown by subprocess.run
    cmd : list(str)
        command [] that was passed into run()
    """
    # TODO: assert e is an error
    stacktrace = traceback.format_exc()
    output_text = (
        "\n# =========================================================\n"
        f"# === exited w/ returncode {getattr(e, 'returncode', None)}. "
        "=============================\n"
        f"# === cmd     : {' '.join(cmd)}\n"
        f"# === e.cmd   : {getattr(e, 'cmd', None)}\n"
        f"# === args : \n\t{getattr(e, 'args', None)} \n"
        f"# === err code: {getattr(e, 'code', None)} \n"
        f"# === descrip : \n\t{getattr(e, 'description', None)} \n"
        f"# === stack_trace: \n\t{stacktrace}\n"
        f"# === std output : \n\t{getattr(e, 'stdout', None)} \n"
        f"# === stderr out : \n\t{getattr(e, 'stderr', None)} \n"
        # f"# === all err obj attributes: \n{dir(e)}"
    )
    if getattr(e, 'original_exception', None) is not None:
        output_text += (
            "# === original exception output: \n\t"
            f"{getattr(e.original_exception, 'output', None)}\n"
            "# === original exception stdout: \n\t"
            f"{getattr(e.original_exception, 'stdout', None)}\n"
            "# === original exception stderr: \n\t"
            f"{getattr(e.original_exception, 'stderr', None)}\n"
        )
    output_text += (
        "# =========================================================\n"
    )
    return output_text
