# PyTorch 开发环境搭建

在使用 Anaconda+VSCode+PyTorch 的工作流中，Anaconda 的核心作用是环境管理和包管理，以下是最常用的指令分类总结：

# 环境管理（核心，推荐为 PyTorch 单独创建环境）

环境隔离能避免不同项目的依赖冲突，是必须掌握的基础。

| 指令 | 作用 | 示例 |

|---|---|---|

| conda create -n <环境名> python=<版本> | 创建新环境（指定 Python 版本） | conda create -n pytorch_env python=3.9（为 PyTorch 创建名为 pytorch_env 的环境，Python3.9） |

| conda activate <环境名> | 激活环境（进入环境） | conda activate pytorch_env（Windows/Linux/macOS 通用，旧版 Linux 可能需要先source ~/.bashrc） |

| conda deactivate | 退出当前环境 | 直接输入，回到 base 环境 |

| conda env list 或 conda info --envs | 查看所有已创建的环境 | 输出会显示环境名称和路径（VSCode 选择解释器时需要路径） |

| conda remove -n <环境名> --all | 删除环境（谨慎使用） | conda remove -n pytorch_env --all |

| conda rename -n <旧名> <新名> | 重命名环境（需先退出环境） | conda rename -n pytorch_env torch_env |

|  |  |  |

# 包管理（安装 / 管理 PyTorch 及依赖）

PyTorch、VSCode 插件依赖（如 numpy、pandas）等均通过包管理指令安装。

| 指令 | 作用 | 示例 |

|---|---|---|

| conda install <包名> | 安装指定包（默认最新版） | conda install numpy（安装 numpy） |

| conda install <包名>=<版本> | 安装指定版本的包 | conda install pandas=1.5.3（安装 1.5.3 版本的 pandas） |

| conda install -c <通道> <包名> | 从指定通道安装（如 PyTorch 官方通道） | 安装 PyTorch（参考官网命令）：conda install pytorch torchvision torchaudio cudatoolkit=11.8 -c pytorch（-c pytorch 指定官方通道，确保版本匹配） |

| conda install -c conda-forge <包名> | 从 conda-forge 通道安装（包更全） | conda install -c conda-forge opencv（安装 OpenCV，conda 默认源可能没有） |

| pip install <包名> | 用 pip 安装（conda 源没有时补充） | pip install matplotlib（pip 和 conda 可混用，优先用 conda） |

| conda update <包名> | 更新指定包 | conda update pytorch（更新 PyTorch 到最新版） |

| conda update --all | 更新当前环境所有包 | 谨慎使用（可能导致依赖冲突） |

| conda remove <包名> | 卸载指定包 | conda remove torchvision |

| conda list | 查看当前环境已安装的所有包 | 可加grep <关键词>筛选（如 `conda list |

# 镜像源配置（加速下载，国内必备）

默认源在国内速度慢，建议配置清华 / 中科大等镜像源（尤其安装 PyTorch 时）。

| 指令 | 作用 | 示例 |

|---|---|---|

| conda config --add channels <源地址> | 添加镜像源 | 添加清华源（常用）：conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/mainconda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/freeconda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forgeconda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch（PyTorch 专属源） |

| conda config --set show_channel_urls yes | 显示包的安装来源（方便排查问题） | 执行后，安装包时会显示从哪个源下载 |

| conda config --remove channels <源地址> | 删除指定镜像源 | conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free |

| conda config --show channels | 查看当前已配置的所有源 | 确认是否添加成功 |

| conda config --remove-key channels | 恢复默认源（镜像源出问题时用） | 重置所有源配置 |

# 其他实用指令

| 指令 | 作用 |

|---|---|

| conda --version 或 conda -V | 查看 conda 版本（确认安装成功） |

| conda update conda | 更新 conda 本身到最新版 |

| conda clean -p | 清理未使用的包缓存（释放空间） |

| conda clean -t | 清理 tar 包缓存 |

| conda clean -a | 清理所有缓存（最彻底，推荐定期执行） |

## 与 VSCode 配合的关键操作

- 激活环境后，在环境中输入code .，可直接启动 VSCode 并关联当前环境（无需手动选择解释器）。

- 若已打开 VSCode，通过 Ctrl+Shift+P 调出命令面板，输入 Python: Select Interpreter，选择 conda环境/pytorch_env 即可关联创建的 PyTorch 环境。

这些指令覆盖了从环境创建、依赖安装到镜像配置的全流程，配合 VSCode 的 Python 插件，可高效搭建 PyTorch 开发环境。安装 PyTorch 时，建议先去PyTorch 官网根据系统、CUDA 版本生成对应安装命令（确保 GPU 支持的兼容性）。

安装jupyter内核(pytorch) 中

pip install ipykernel

conda install nb_conda_kernels
