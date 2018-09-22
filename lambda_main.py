try:
        import boto3
        import json
        import os
        from collections import OrderedDict
        from datetime import date, timedelta, datetime
        from botocore.exceptions import ClientError
        from collections import OrderedDict
except ImportError:
        HAS_BOTO = False

client = boto3.client('ec2')
sns = boto3.client('sns')
TODAY = date.today()

class Ec2List:
        def __init__(self, ec2Id = None, name = None, noReboot = None, expire = None, createdDate = None, imageId = None):
                self._ec2Id = ec2Id
                self._name = name
                self._noReboot = noReboot
                self._expire = expire
                self._createdDate = str(TODAY)
                self._imageId = imageId

        @classmethod
        def get_json_file(cls):
                result = []
                try:
                        with open('./ec2List.json', 'r') as f:
                                createImageList = json.load(f)
                        for each in createImageList['list']:
                                createAmiManager = cls(each['ec2Id'], each['name'], each['noReboot'], each['expire'], TODAY)
                                result.append(createAmiManager)
                        return result
                except IOError as e:
                        print('Exception - Failed EC2 List read file: {}'. format(e))
                        return None

        def get_ec2_list(self):
                return self

        @property
        def imageId(self):
                return self._imageId

        @imageId.setter
        def imageId(self, imageId):
                self._imageId = imageId


def create_amis(list):
    for each in list:
        ec2List = each.get_ec2_list()
        try:
            response = client.create_image(
                Description='auto-backup-image',
                DryRun=False,
                InstanceId=ec2List._ec2Id,
                Name=ec2List._name + '_' + ec2List._createdDate,
                NoReboot=ec2List._noReboot
            )
            ec2List._imageId = response['ImageId']
        except ClientError as e:
            print('Exceptioin - Failed Create Image: {}'.format(e))
        if ec2List._imageId != None:
            try:
                response = client.create_tags(
                    DryRun=False,
                    Resources=[
                        ec2List._imageId,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': ec2List._name + '_' + ec2List._createdDate
                        },
                        {
                            'Key': 'ec2Id',
                            'Value': ec2List._ec2Id
                        },
                        {
                            'Key': 'createdDate',
                            'Value': ec2List._createdDate
                        },
                        {
                            'Key': 'expire',
                            'Value': ec2List._expire
                        },
                        {
                            'Key': 'backupManager',
                            'Value': 'auto'
                        },
                        {'Key': 'imageId',
                         'Value': ec2List._imageId

                         }
                    ]
                )
            except ClientError as e:
                print('Exceptioin - Failed Create Tag: {}'.format(e))
    return None

def delete_amis():
        createdDate = None
        expire = None
        imageId = None
        convertDate = None
        deleteImageList = []
        try:
            response = client.describe_images(
                Filters=[
                    {
                        'Name': 'tag:backupManager',
                        'Values': [
                            'auto'
                        ]
                    }
                ],
                DryRun=False
            )
        except ClientError as e:
            print('Exceptioin - Failed Describe Tag: {}'.format(e))

        for each in response['Images']:
            for tags in each['Tags']:
                if tags['Key'] == 'createdDate':
                    createdDate = tags['Value']
                if tags['Key'] == 'expire':
                    expire = tags['Value']
                if tags['Key'] == 'imageId':
                    imageId = tags['Value']
            convertDate = datetime.strptime(createdDate, '%Y-%m-%d').date()
            compare = TODAY - convertDate
            if (int(compare.days) >= int(expire)):
                try:
                    client.deregister_image(
                        ImageId=imageId,
                        DryRun=False
                    )
                except ClientError as e:
                    print('Exception: Failed Delete AMI {}'.format(e))
                deleteImageList.append(each)
        return deleteImageList

def sendMail(ec2InstanceList, deletedImageList):
        createdImageList = []
        failedImageList = []
        for each in ec2InstanceList:
            ec2List = each.get_ec2_list()
            result = {
                'ec2Id': ec2List._ec2Id,
                'name': ec2List._name,
                'noReboot': ec2List._noReboot,
                'expire': ec2List._expire,
                'createdDate': str(TODAY),
                'imageId': ec2List._imageId
            }
            if ec2List._imageId != None:
                createdImageList.append(result)
            else:
                failedImageList.append(result)

        print('Created Image List: ' + json.dumps(createdImageList))
        print('failed Image List: ' + json.dumps(failedImageList))
        print('Deleted Image List: ' + json.dumps(deletedImageList))
        try:
            response = sns.publish(
                TopicArn='arn:aws:sns:ap-northeast-2:557652101750:ec2_ami_managing',
                Subject='EC2 AMI MANAGING',
                Message='Created Image LIST: ' + json.dumps(createdImageList) + '\n\n\n' +
                        'Failed Image LIST: ' + json.dumps(failedImageList) + '\n\n\n'
                                                                              'Deleted Image LIST: ' + json.dumps(
                    deletedImageList) + '\n\n\n'
            )
        except ClientError as e:
            print('Exception: Failed Send Message {}'.format(e))

def main():
    ec2list = Ec2List.get_json_file()
    create_amis(ec2list)
    delete_image_list = delete_amis()
    sendMail(ec2list, delete_image_list)

if __name__ == '__main__':
    main()

def handler(even, context):
    main()


