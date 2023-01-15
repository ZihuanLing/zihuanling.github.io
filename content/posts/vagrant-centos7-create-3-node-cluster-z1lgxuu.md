---
title: vagrant + centos7创建3节点集群
slug: vagrant-centos7-create-3-node-cluster-z1lgxuu
url: /post/vagrant-centos7-create-3-node-cluster-z1lgxuu.html
tags: []
categories: []
lastmod: '2023-01-15 21:33:12'
toc: true
keywords: ''
description: >-
  vagrantcentos创建节点集群坑设置节点的网络的时候需要给一个属性name​确保节点启动的时候集群里面的节点会绑定到同一个网络平面_nodevmnetwork​为了防止节点启动的时候端口被随机分配绑定宿主机端口我们可以配置将其转发到一个固定的端口_nodevmnetwork​配置文件_#vagrantfilevagrantconfigure()do_config_#configvmnetworkauto_config_false()eachdo_i_configvmdefinedo_node_#设
isCJKLanguage: true
---

# vagrant + centos7创建3节点集群

## 坑

1. 设置节点的网络的时候，需要给一个属性`name`​，确保节点启动的时候，集群里面的节点会绑定到同一个网络平面：**`node.vm.network "private_network", name: "VirtualBox Host-Only Enthernet Adapter"`**​
2. 为了防止节点启动的时候，22端口被随机分配绑定宿主机端口，我们可以配置将其转发到一个固定的端口：`node.vm.network "forwarded_port", guest: 22, host: "230#{i}"`​，需要注意的是，需要先将原来的ssh转发端口禁用掉：`node.vm.network "forwarded_port", guest: 22, host: 2222, id: "ssh", disabled: "true"`​

配置文件：

```Vagrant
# Vagrantfile
Vagrant.configure("2") do |config|

    # config.vm.network "private_network", auto_config: false

        (1..3).each do |i|

                config.vm.define "node#{i}" do |node|

                    # 设置虚拟机的Box
            node.vm.box = "generic/centos7"

            # 设置虚拟机的主机名
            node.vm.hostname="node#{i}"

            # 设置虚拟机的IP，绑定一个固定的网卡，确保
            node.vm.network "private_network", ip: "192.168.59.10#{i}", name: "VirtualBox Host-Only Ethernet Adapter"

            # 设置端口转发
            node.vm.network "forwarded_port", guest: 22, host: 2222, id: "ssh", disabled: "true"
            node.vm.network "forwarded_port", guest: 22, host: "230#{i}"
            node.vm.network "forwarded_port", guest: 2181, host: "218#{i}"

            # 设置主机与虚拟机的共享目录
            node.vm.synced_folder "D:/Vagrants/share", "/home/vagrant/share"

            # VirtaulBox相关配置
            node.vm.provider "virtualbox" do |v|

                # 设置虚拟机的名称
                v.name = "node#{i}"

                # 设置虚拟机的内存大小
                v.memory = 6144

                # 设置虚拟机的CPU个数
                v.cpus = 1
            end

                end
        end
end
```

‍
