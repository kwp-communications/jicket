"""
This script deploys Jicket as an ECS Fargate service.
In order for this to work you need to manually create a VPC with an internet gateway. You also need to create a
cloudwatch group called '/ecs/jicket-task'.
"""

from troposphere import *
from troposphere import ecs


# Variables
# ===========
jicketsubnet = "SETME"
executionrolearn = "SETME"    # Role with AmazonECSTaskExecutionRolePolicy

jicketimaphost = "SETME"
jicketimapuser = "SETME"
jicketimappass = "SETME"

jicketsmtphost = "SETME"

jicketticketaddress = "SETME"

jicketjiraurl = "SETME"
jicketjirauser = "SETME"
jicketjirapass = "SETME"
jicketjiraproject = "SETME"

jicketthreadtemplate = "/etc/jicket/threadtemplate.html"

t = Template("Jicket ECS Deployment")

# ECS Cluster
# =============
cluster = ecs.Cluster("JicketCluster")
cluster.ClusterName = "Jicket"

t.add_resource(cluster)

# ECS Task Definition
# =====================
taskdef = ecs.TaskDefinition("JicketTask")

contdef = ecs.ContainerDefinition()
contdef.Cpu = 0
contdef.Environment = [
    ecs.Environment(Name="JICKET_IMAP_HOST", Value=jicketimaphost),
    ecs.Environment(Name="JICKET_JIRA_USER", Value=jicketjirauser),
    ecs.Environment(Name="JICKET_TICKET_ADDRESS", Value=jicketticketaddress),
    ecs.Environment(Name="JICKET_SMTP_HOST", Value=jicketsmtphost),
    ecs.Environment(Name="JICKET_JIRA_PASS", Value=jicketjirapass),
    ecs.Environment(Name="JICKET_JIRA_PROJECT", Value=jicketjiraproject),
    ecs.Environment(Name="JICKET_JIRA_URL", Value=jicketjiraurl),
    ecs.Environment(Name="JICKET_THREAD_TEMPLATE", Value=jicketthreadtemplate),
    ecs.Environment(Name="JICKET_IMAP_PASS", Value=jicketimappass),
    ecs.Environment(Name="JICKET_IMAP_USER", Value=jicketimapuser),
]
contdef.Image = "kwpcommunications/jicket:latest"
contdef.MemoryReservation = 512
contdef.Name = "jicket"
logconf = ecs.LogConfiguration()
logconf.LogDriver = "awslogs"
logconf.Options = {
    "awslogs-group": "/ecs/jicket-task",
    "awslogs-region": "eu-central-1",
    "awslogs-stream-prefix": "ecs"
}
contdef.LogConfiguration = logconf

taskdef.ContainerDefinitions = [contdef]
taskdef.Cpu = "256"
taskdef.Family = "jicket-task"
taskdef.RequiresCompatibilities = [
    "FARGATE"
]
taskdef.NetworkMode = "awsvpc"
taskdef.Memory = "512"
taskdef.ExecutionRoleArn = executionrolearn

t.add_resource(taskdef)

# ECS Service
# =============
service = ecs.Service("JicketService")
service.Cluster = Ref(cluster.title)
service.DesiredCount = 1
service.LaunchType = "FARGATE"
service.ServiceName = "Jicket-Service"
service.TaskDefinition = Ref(taskdef.title)
vpcconf = ecs.AwsvpcConfiguration()
vpcconf.Subnets = [jicketsubnet]
vpcconf.AssignPublicIp = "ENABLED"
service.NetworkConfiguration = ecs.NetworkConfiguration(
    AwsvpcConfiguration=vpcconf
)

t.add_resource(service)


t_json = t.to_json()
with open("jicket-ecs.json", "w") as f:
    print(t_json)
    f.write(t_json)
