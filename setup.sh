#!/bin/bash

set -euo pipefail

KRWDIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
WORKDIR=`pwd`
ARCH=`uname -m`
VENVNAME="quickfuzz-$ARCH"

if [[ ! "$WORKDIR" -ef "$KRWDIR" ]]; then
	echo "Run the script from the retrowrite root directory: cd $KRWDIR && bash ./setup.sh"
	exit 1
fi

if [[(( $# == 1 )&& ("$1" == "help")  )]]; then
  echo "Usage of the script : $0 [kernel(optional)]"
  exit
fi

if [[ ! -e "./$VENVNAME" ]]; then

  python3 -m venv $VENVNAME

  # Work around a virtualenv bug :\
  set +u
  source $VENVNAME/bin/activate
  set -u
  pip3 install --upgrade wheel
  pip3 install --upgrade pip
  pip3 install -r requirements.txt


  echo "source $(pwd)/$VENVNAME/bin/postactivate" >> $VENVNAME/bin/activate
  echo "export PYTHONPATH=\"$(pwd)\"" > $VENVNAME/bin/postactivate


  #git submodule update --init --checkout third-party/capstone
  cd third-party/capstone
  make -j `nproc`
  cd bindings/python/ && make -j `nproc` && make install


  set +u
  deactivate
  set -u
  cd $WORKDIR
  ln -s $(pwd)/quickfuzz-$ARCH.py $(pwd)/$VENVNAME/bin/quickfuzz

  echo "[+] All done and ready to go"
  echo "[ ] You can start run : source ./$VENVNAME/bin/activate"

else
  echo "virtualenv already setup."

fi

# install kernel version
if [[ (( $# == 1 )&&  ("$1" == 'kernel')) ]]; then
  export GOROOT="$KRWDIR/$VENVNAME/go1.14"
  echo "export PYTHONPATH=\"$(pwd)\"" > $KRWDIR/$VENVNAME/bin/postactivate
  echo "export GOROOT=\"$GOROOT\"" >> $KRWDIR/$VENVNAME/bin/postactivate
  echo "export PATH=\"$GOROOT/bin:$KRWDIR/cftool:\$PATH\"" >> $KRWDIR/$VENVNAME/bin/postactivate
  export PATH="$GOROOT/bin:$KRWDIR/cftool:$PATH"

  	# Download Go
	# installing go into the venv bin
	if [[ ! -e "$KRWDIR/$VENVNAME/go1.14" ]]; then
		pushd "$KRWDIR/$VENVNAME/"

			wget https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz
			tar -xf go1.14.2.linux-amd64.tar.gz
			rm go1.14.2.linux-amd64.tar.gz
			mv go go1.14

			# export GOPATH="$KRWDIR/retro/go"
			# export GOROOT="$KRWDIR/retro/go1.14/"
			#export PATH="$GOPATH/bin:$GOROOT/bin:$KRWDIR/cftool:$PATH"

			pushd "$KRWDIR/cftool"
				go build
			popd
		popd
	else
	  echo "Go environment already setup"
	fi


fi

