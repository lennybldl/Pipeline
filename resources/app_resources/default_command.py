"""The commands to {name} the member."""


def execute(member, *args, **kwargs):
    """The commands to execute when the {name} command is called.

    Arguments:
        member (Member): The interface will automaticaly call the script giving the
            member the script need to be executed on.
    """
    print("{title}")
