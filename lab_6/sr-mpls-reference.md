### SR-MPLS Reference

Linux and VPP support both SRv6 and MPLS dataplane operations. For the purposes of this lab we're only using SRv6.

There is no Linux "SR-MPLS" per se, but from the host's perspective its just MPLS labels, so one can use Linux's iproute2 MPLS implemenation. Ubuntu iproute2 manpage: 

https://manpages.ubuntu.com/manpages/jammy/man8/ip-route.8.html

### Enable XRd forwarding of SR-MPLS traffic coming from Linux hosts
In order to forward inbound labeled packets received from a network attached host or other endpoint we'll need to enable MPLS forwarding on xrd01's and xrd07's VM-facing interfaces:

1. Enable MPLS forwarding on the VM-facing interfaces on both xrd01 and xrd07: 

    ```
    mpls static
    int gigabitEthernet 0/0/0/0
    commit

    ```
    Validate MPLS forwarding is enabled:
    ```
    show mpls interface
    ```
    Expected output:
    ```
    Fri Dec 23 23:24:11.146 UTC
    Interface                  LDP      Tunnel   Static   Enabled 
    -------------------------- -------- -------- -------- --------
    GigabitEthernet0/0/0/0     No       No       Yes      Yes
    GigabitEthernet0/0/0/1     No       No       No       Yes
    GigabitEthernet0/0/0/2     No       No       No       Yes
    ```

### Enable SR-MPLS label operations on Linux host

1. For host-based SR/MPLS the Linux MPLS modules aren't loaded by default, so we'll run *modprobe* commands to enable them:

    ```
    sudo modprobe mpls_router
    sudo modprobe mpls_iptunnel
    ```
    Unfortunately the modprobe commands don't return any response to the command line. So:

2. Validate MPLS modules are loaded:
   
   ```
   lsmod | grep mpls
   ```
   Output should look something like this:
   ```
   cisco@rome:~$ lsmod | grep mpls
    mpls_iptunnel          20480  0                    <----- Currently no MPLS tunnels/routes configured
    mpls_router            40960  1 mpls_iptunnel
    ip_tunnel              24576  1 mpls_router
   ```
  
   - Reference: https://linuxize.com/post/lsmod-command-in-linux/

