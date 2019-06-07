#!/usr/bin/env python3

import bumper
import argparse
import asyncio
import platform
import os
import subprocess
import sys


def first_run():
    yes = {"yes", "y", "ye", ""}
    print("")
    create_cert = input(
        "No certificates found, would you like to create them automatically? (y/n): "
    ).lower()
    if create_cert in yes:
        print("Creating certificates")
        odir = os.path.dirname(os.path.realpath(__file__))
        os.chdir("certs")
        if platform.system().lower() == "windows":
            # run for win
            subprocess.run(
                [os.path.join("..", "create_certs", "create_certs_windows.exe")]
            )
        elif platform.system().lower() == "darwin":
            # run on mac
            subprocess.run([os.path.join("..", "create_certs", "create_certs_osx")])
        elif platform.system().lower() == "linux":
            if "arm" in platform.machine().lower():
                # run for pi
                subprocess.run([os.path.join("..", "create_certs", "create_certs_rpi")])
            else:
                # run for linux
                subprocess.run(
                    [os.path.join("..", "create_certs", "create_certs_linux")]
                )
        else:
            print("Can't determine platform. Create certs manually and try again.")
            exit(1)

        print("Certificates created")
        os.chdir(odir)
        os.execv(sys.executable, ["python"] + sys.argv)  # Start again

    else:
        print("Can't continue without certificates, please create some then try again.")
        exit(1)


def main():
    try:

        if not (
            os.path.exists(bumper.ca_cert)
            and os.path.exists(bumper.server_cert)
            and os.path.exists(bumper.server_key)
        ):
            first_run()

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--listen", type=str, default=None, help="start serving on address"
        )
        parser.add_argument(
            "--announce",
            type=str,
            default=None,
            help="announce address to bots on checkin",
        )
        parser.add_argument("--debug", action="store_true", help="enable debug logs")
        args = parser.parse_args()

        if args.debug:
            bumper.bumper_debug = True

        if args.listen:
            bumper.bumper_listen = args.listen

        if args.announce:
            bumper.bumper_announce_ip = args.announce

        asyncio.run(bumper.start())

    except KeyboardInterrupt:
        bumper.bumperlog.info("Keyboard Interrupt!")
        pass

    except Exception as e:
        bumper.bumperlog.exception(e)
        pass

    finally:
        asyncio.run(bumper.shutdown())


if __name__ == "__main__":
    main()

