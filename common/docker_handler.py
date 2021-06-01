#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : docker_handler.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/4/7 13:44
# @Desc  :
import docker


class DockerHandler:

    def __init__(self):
        self.client = docker.APIClient(base_url='http://10.0.0.10:2375')

    # def __del__(self):
    #     self.client.close()

    def create_lambda_container(self, image):
        container = self.client.create_container(image=image, command="bin/bash -c 'source optimus_env/bin/activate;cd /gaofzhan_1/;python test.py'", volumes=['/gaofzhan_1/test.py'],
                                                 working_dir='/', host_config=self.client.create_host_config(privileged=True, binds={'/gaofzhan/test.py': {"bind": '/gaofzhan_1/test.py', "mode": "rw", }, }, ))
        return container

    def start_lambda_container(self, container_id):
        self.client.start(container_id)

    def get_container_log(self, container_id):
        log = self.client.logs(container_id)
        return log

    def del_container(self, container_id):
        self.client.remove_container(container_id)


if __name__ == '__main__':
    res = DockerHandler().create_lambda_container('optimus-exec-container:v1.2.1')
    print(res)
    cid = res['Id']
    DockerHandler().start_lambda_container(cid)
    DockerHandler().client.wait(cid)
    res = DockerHandler().get_container_log(cid)
    # res = DockerHandler().get_container_log('de73c51ced95')
    DockerHandler().del_container(cid)
    print(res)
