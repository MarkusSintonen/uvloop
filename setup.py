import os
import subprocess
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


LIBUV_DIR = os.path.join(os.path.dirname(__file__), 'vendor', 'libuv')


class libuv_build_ext(build_ext):
    def build_libuv(self):
        cflags = '-fPIC'
        env = os.environ.copy()

        env['CFLAGS'] = ('-fPIC ' +
                         env.get('CFLAGS', '') +
                         ' ' +
                         env.get('ARCHFLAGS', ''))

        subprocess.run(['sh', 'autogen.sh'], cwd=LIBUV_DIR, env=env)
        subprocess.run(['./configure'], cwd=LIBUV_DIR, env=env)
        subprocess.run(['make', '-j4'], cwd=LIBUV_DIR, env=env)

    def build_extensions(self):
        libuv_lib = os.path.join(LIBUV_DIR, '.libs', 'libuv.a')
        if not os.path.exists(libuv_lib):
            self.build_libuv()
        if not os.path.exists(libuv_lib):
            raise RuntimeError('failed to build libuv')

        self.extensions[0].extra_objects.extend([libuv_lib])
        self.compiler.add_include_dir(os.path.join(LIBUV_DIR, 'include'))

        if sys.platform.startswith('linux'):
            self.compiler.add_library('rt')
        elif sys.platform.startswith('freebsd'):
            self.compiler.add_library('kvm')

        super().build_extensions()


setup(
    name='uvloop',
    version='0.0.1',
    packages=['uvloop'],
    cmdclass = {'build_ext': libuv_build_ext},
    ext_modules=[
        Extension(
            "uvloop.loop",
            sources = [
                "uvloop/loop.c",
            ]
        ),
        Extension(
            "uvloop.idle",
            sources = [
                "uvloop/idle.c",
            ]
        ),
        Extension(
            "uvloop.signal",
            sources = [
                "uvloop/signal.c",
            ]
        ),
        Extension(
            "uvloop.async_",
            sources = [
                "uvloop/async_.c",
            ]
        ),
        Extension(
            "uvloop.timer",
            sources = [
                "uvloop/timer.c",
            ]
        )
    ],
    provides=['uvloop'],
    include_package_data=True
)