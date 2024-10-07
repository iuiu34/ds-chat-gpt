import re
import subprocess

import yaml


def get_release_candidate(filename):
    with open(filename) as f:
        data = f.read()

    # Find the current version in the file
    match = re.search(r'v[0-9]+\.[0-9]+\.[0-9]+(rc[0-9]+)?', data)

    if match is None:
        print("No version found in the file.")
        return

    current_version = match.group()

    # Check if the version contains a release candidate number
    if 'rc' in current_version:
        # Split the version into base version and release candidate number
        base_version, rc_number = re.match(r'(v[0-9]+\.[0-9]+\.[0-9]+rc)([0-9]+)', current_version).groups()

        # Increment the release candidate number
        new_rc_number = int(rc_number) + 1

        # Combine the base version and new release candidate number to form the new version
        new_version = base_version + str(new_rc_number)
    else:
        # If the version doesn't contain a release candidate number, append 'rc1' to it
        new_version = current_version + 'rc1'

    # Replace the current version with the new version
    data_ = data.replace(current_version, new_version)

    # Write the updated data back to the file
    with open(filename, 'w') as f:
        f.write(data_)


def run(cmd):
    print(cmd)
    cmd = f"sh {cmd}"
    subprocess.run(cmd, check=True)


def get_check_branch(dev: bool):
    if dev:
        branch = 'dev'
    else:
        branch = 'master'

    cmd = f"git branch"
    branch_ = subprocess.run(cmd, check=True, capture_output=True)
    branch_ = branch_.stdout.decode().split('\n')
    branch_ = [v for v in branch_ if '*' in v][0]
    branch_ = branch_.replace('*', '').strip()
    if branch != branch_:
        raise ValueError(f"Branch is not {branch}. Run: \ngit checkout {branch}\ngit merge {branch_}")


def deploy_app(repo,
               docker: bool = True,
               cloud_run: bool = False,
               app_engine: bool = False,
               frontend: bool = False,
               job: bool = False,
               dev: bool = False,
               tox: bool = False,
               check_branch: bool = False,
               ):
    print("deploy_app")
    print(vars())

    if check_branch:
        get_check_branch(dev)

    if cloud_run and app_engine:
        raise ValueError('Cannot deploy to both Cloud Run and App Engine. Choose one.')

    if job and app_engine:
        raise ValueError('Cannot deploy job to App Engine. Choose Cloud Run.')

    if app_engine:
        filename = 'app.yaml'
    else:
        filename = 'service.yaml'

    if dev:
        filename = filename.split('.')
        filename = f"{filename[0]}_dev.{filename[1]}"

    if docker and cloud_run:
        get_release_candidate(filename)
        if job:
            filename_job = filename.replace('service', 'job')
            get_release_candidate(filename_job)

    with open(filename) as f:
        app_config = yaml.full_load(f)

    if app_engine:
        image_url = app_config['env_variables']['IMAGE_URL']
    else:
        image_url = app_config['spec']['template']['spec']['containers'][-1]['image']

    if tox:
        cmd = 'tox'
        run(cmd)

    if docker:
        cmd = 'container/vm_docker_build.sh'
        cmd = f'{cmd} {image_url} {repo}'
        run(cmd)

    if docker and frontend:
        repo = f'{repo}/frontend'
        image_url = app_config['spec']['template']['spec']['containers'][0]['image']
        cmd = 'container/vm_docker_build.sh'
        cmd = f'{cmd} {image_url} {repo}'
        run(cmd)

    if cloud_run:
        service_name = app_config['metadata']['name']
        # cmd = f'gcloud run services delete {service_name} -q'
        # run(cmd)
        cmd = f"gcloud run services replace {filename}"
        run(cmd)
        cmd = f'gcloud run services add-iam-policy-binding {service_name} ' \
              f'--member="allUsers" --role="roles/run.invoker"'
        run(cmd)
    elif app_engine:
        cmd = f"gcloud app deploy {filename} -q --image-url={image_url}"
        run(cmd)

    if job:
        cmd = "gcloud run jobs replace job.yaml"
        run(cmd)
