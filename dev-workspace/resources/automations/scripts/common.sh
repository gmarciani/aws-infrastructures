#!/bin/bash

function info() {
    echo "[INFO] $1"
}

function warn() {
    echo "[WARN] $1"
}

function fail() {
    echo "[ERROR] $1" >&2
    exit 1
}
