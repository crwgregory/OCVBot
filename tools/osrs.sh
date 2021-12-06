#!/usr/bin/env bash

# Wrapper script for downloading and running the OSRS Java client on Linux.
# Requires p7zip, wget, and java (openjdk must be <= 13, see wiki link).
#
# See for more info: https://oldschool.runescape.wiki/w/Linux_game_installation_guide

# Arguments can be added to the Java applet by passing them on the
#   command line, e.g. `osrs.sh "-Dhttp.proxyHost=10.0.0.1 -Dhttp.proxyPort=8008"`

# The path to the Java executable you wish to use.
# Override default by setting an env var OSRS_PATH_JAVA to your systems path
#   or by supplying it in the command `OSRS_PATH_JAVA=/my/path ./tools/osrs.sh`
readonly java_path="${OSRS_PATH_JAVA:-/usr/lib/jvm/java-11-openjdk/bin/java}"

# These varaiables are unlikely to change.
readonly server="http://oldschool.runescape.com/jav_config.ws"
readonly dmg_url="https://www.runescape.com/downloads/OldSchool.dmg"

install_location="${HOME}/.local/share/osrs"

# ------------------------------------------------------------------------

set -euo pipefail

# Strip trailing slashes.
install_location="$(printf "%s\n" "${install_location%/}")"

print() {
    printf \
        "\n%s %s\n\n" \
        "[$(date +%F_%T)]" \
        "INFO: $* ####################################################################################################"
}

cleanup() {
    print "Cleaning up"
    rm -rf -- \
        "${HOME}/random.dat" \
        "${HOME}/jagex_cl_oldschool_LIVE.dat" \
        "${HOME}/jagexappletviewer.preferences"
    # Hide the cache directory if it's not hidden.
    [[ -d "${HOME}/jagexcache" ]] && mv -f -- "${HOME}/jagexcache" "${HOME}/.jagexcache"
}

launch_applet() {
    print "Launching Java applet"
    "${java_path}" \
        $* \
        -Djava.class.path="./jagexappletviewer.jar" \
        -Dsun.java2d.nodraw=true \
        -Dcom.jagex.config="${server}" \
        -Xmx512m \
        -Xms512m \
        -Xss2m \
        -XX:CompileThreshold=1500 \
        jagexappletviewer "."
}

# Clean up when killed or exiting.
trap cleanup EXIT

# Check for missing software.
if ! hash wget 2>/dev/null; then echo "wget missing!" && exit 1; fi
if ! hash 7z 2>/dev/null; then echo "7z missing!" && exit 1; fi

# Un-hide the cache directory if it's hidden.
[[ -d "${HOME}/.jagexcache" ]] && mv -f -- "$HOME/.jagexcache" "$HOME/jagexcache"

# Try to enter the JAR directory and run the applet. If the JAR directory
#   doesn't exist, then attempt to download the applet.
print "Attempting to enter Java applet directory"
if cd "${install_location}/osrs.dmg/Old School RuneScape/Old School RuneScape.app/Contents/Java"; then
    launch_applet $*

else

    # Download and extract the JAR file if it isn't present.
    print "Pulling image"
    [[ ! -d "${install_location}" ]] && mkdir -p -- "${install_location}"
    wget --no-check-certificate --no-verbose "${dmg_url}" --output-document="${install_location}/osrs.dmg.7z"

    # Extract the JAR file from the DMG archive.
    print "Extracting image"
    7z x -y "${install_location}/osrs.dmg.7z" -o"${install_location}/osrs.dmg/"

    # Try running the applet again.
    cd "${install_location}/osrs.dmg/Old School RuneScape/Old School RuneScape.app/Contents/Java"
    launch_applet $*

fi

exit 0
