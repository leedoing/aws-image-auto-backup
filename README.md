# AWS EC2 Imsage Auto Backup Using Lambda, CloudWatchEvent
> Using Lambda Function with python 3.6

### IAM Policy for Lambda Role
```js
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": "arn:aws:ec2:*::image/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DeregisterImage",
                "logs:CreateLogStream",
                "sns:Publish",
                "ec2:CreateImage",
                "logs:PutLogEvents",
                "logs:CreateLogGroup"
            ],
            "Resource": "*"
        }
    ]
}

```

### ec2List.json Config
```js
{
"list":[
	{"ec2Id":"i-0b4947ddfd80496ee", "name":"web", "noReboot":true, "expire":"7"},
	{"ec2Id":"i-08bafac12c7892301", "name":"db", "noReboot":true, "expire":"3"},
	{"ec2Id":"i-023ed8c9d4b97b14a", "name":"app", "noReboot":true, "expire":"1"}
	]
}
```

### Lambda Run Logs
```js
Created Image List: [
{
    "ec2Id": "i-0b4947ddfd80496ee",
    "name": "web",
    "noReboot": true,
    "expire": "7",
    "createdDate": "2018-09-22",
    "imageId": "ami-0c04ec5874f1a4977"
},
	...
{
    "ec2Id": "i-023ed8c9d4b97b14a",
    "name": "app",
    "noReboot": true,
    "expire": "1",
    "createdDate": "2018-09-22",
    "imageId": "ami-00a96d7622d7d3b29"
}
]

Failed Image List: [
{
    "ec2Id": "i-0b4947ddfd80496ee",
    "name": "web",
    "noReboot": true,
    "expire": "7",
    "createdDate": "2018-09-22",
    "imageId": null
},
	...
{
    "ec2Id": "i-023ed8c9d4b97b14a",
    "name": "app",
    "noReboot": true,
    "expire": "1",
    "createdDate": "2018-09-22",
    "imageId": null
}
]

Deleted Image List: [
{
    "Architecture": "x86_64",
    "CreationDate": "2018-09-21T05:04:28.000Z",
    "ImageId": "ami-0dffad17281f6ec89",
    "ImageLocation": "557652101750/app_2018-09-21",
    "ImageType": "machine",
     ...
    "SriovNetSupport": "simple",
    "Tags": [
        {
            "Key": "expire",
            "Value": "1"
        },
        {
            "Key": "backupManager",
            "Value": "auto"
        },
        {
            "Key": "Name",
            "Value": "app_2018-09-21"
        },
        {
            "Key": "createdDate",
            "Value": "2018-09-21"
        },
        {
            "Key": "ec2Id",
            "Value": "i-023ed8c9d4b97b14a"
        },
        {
            "Key": "imageId",
            "Value": "ami-0dffad17281f6ec89"
        }
    ],
    "VirtualizationType": "hvm"
}
]
```
