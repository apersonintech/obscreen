#!/bin/bash

MOUNT_DIR=$2

get_partition_size() {
    local partition=$1
    lsblk -bno SIZE "$partition"
}

find_largest_partition() {
    local device=$1
    local largest_partition=""
    local largest_size=0

    for partition in $(lsblk -lnp "$device" | awk '{print $1}'); do
        size=$(get_partition_size "$partition")
        if (( size > largest_size )); then
            largest_size=$size
            largest_partition=$partition
        fi
    done

    echo $largest_partition
}

# Get device (e.g., /dev/sda)
base_device=$(echo $1 | sed 's/[0-9]*$//')
largest_partition=$(find_largest_partition "$base_device")

# Mount largest partition
if [ -n "$largest_partition" ]; then
    mkdir -p "$MOUNT_DIR"
    mount_options="relatime"
    if blkid -o value -s TYPE "$largest_partition" | grep -qE "vfat|ntfs"; then
        mount_options="$mount_options,gid=100,dmask=000,fmask=111,utf8"
        if blkid -o value -s TYPE "$largest_partition" | grep -q "ntfs"; then
            systemd-mount -t ntfs-3g --no-block --automount=yes --collect -o $mount_options "$largest_partition" "$MOUNT_DIR"
        else
            systemd-mount -t auto --no-block --automount=yes --collect -o $mount_options "$largest_partition" "$MOUNT_DIR"
        fi
    else
        systemd-mount -t auto --no-block --automount=yes --collect -o $mount_options "$largest_partition" "$MOUNT_DIR"
    fi
    logger "Mounted $largest_partition with filesystem type $(blkid -o value -s TYPE "$largest_partition")"
fi
