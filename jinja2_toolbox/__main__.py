from . import cli

try:
    cli.main()
except KeyboardInterrupt:
    exit(0)
