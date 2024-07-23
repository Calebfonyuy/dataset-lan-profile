"""This profile creates a lan with access to the same dataset.
The default dataset is the vm_images dataset

Instructions:
Ensure that the dataset is still available before launching an experiment. """

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Client image list
imageList = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
]

nfsLanName    = "nfsLan"
nfsDirectory  = "/nfs"

pc.defineParameter("resourceTypes", "All Client Types",
                   portal.ParameterType.STRING, "d820")

pc.defineParameter("osImage", "Select OS image for servers",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList)

pc.defineParameter("dataset", "Dataset URN",
                   portal.ParameterType.STRING, 
                   "urn:publicid:IDN+emulab.net:dlock+stdataset+vm_images")

# Always need this when using parameters
params = pc.bindParameters()

# Storage file system goes into a local (ephemeral) blockstore.
nfsBS = request.RemoteBlockstore("DSNode", nfsDirectory)
nfsBS.dataset = params.dataset

resourceTypes = params.resourceTypes.split(',')

ip_count = 1
ifaces = []

for c_type in resourceTypes:
    nfsClient = request.RawPC("node-"+str(ip_count))
    nfsClient.disk_image = params.osImage
    nfsClient.hardware_type = c_type
    nfsClient.routable_control_ip = True
    c_iface = nfsClient.addInterface()
    ifaces.append(c_iface)
    ip_count = ip_count + 1


# The NFS network. All these options are required.
nfsLan = request.LAN(nfsLanName)
# Must provide a bandwidth. BW is in Kbps
nfsLan.bandwidth         = 100000
nfsLan.best_effort       = True
nfsLan.vlan_tagging      = True
nfsLan.addInterface(nfsBS.interface)
for iface in ifaces:
    nfsLan.addInterface(iface)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
