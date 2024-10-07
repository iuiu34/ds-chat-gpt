import fire

from edo.chat_gpt._core_utils.deploy_app import deploy_app


def deploy_app_(
        docker: bool = True,
        cloud_run: bool = False,
        app_engine: bool = False,
        frontend: bool = False,
        job: bool = False,
        dev: bool = False,
        tox: bool = False,
        check_branch: bool = False,
        repo='ds-chat-gpt',

):
    args = locals()
    deploy_app(**args)


def main():
    """Execute main program."""
    fire.Fire(deploy_app_)
    print('\x1b[6;30;42m', 'Success!', '\x1b[0m')


if __name__ == "__main__":
    main()
