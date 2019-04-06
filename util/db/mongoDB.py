import pymongo
from pymongo import MongoClient

class Database(object):
    def __init__(self):
        print "Connecting to Mongo"
        self.mClient = MongoClient('mongodb://localhost:27017/').test

    # Store data in both Mongo and Redis
    def store_data(self, id, data):
#        if DEBUG:
#            print "Inside store data. Sotring data to Mongo and Redis with id : {}".format(id)

        try:
            mResult = self.mClient.files.insert({'_id':id, 'data':data});
            print "Writing to Mongo was successful"
        except pymongo.errors.DuplicateKeyError:
            print "Already exists in Mongo"
            mResult = self.mClient.files.update({'_id':id},{'$set': {'data':data}})

        return self.rClient.set(id, data)

    # Check if data is available in Redis. If not, check in Mongo
    def is_data_available(self, id):
        print "Checking availability"
        if self.rClient.get(id):
            print "Available in Redis"
            return True
        elif self.mClient.files.find({'_id':id}).limit(1).count() > 0:
            print "Available in Mongo"
            return True
        else:
            print "Unavailable in both"
            return False

    # Delete data from both Mongo and Redis
    def delete_data(self, id):
        try:
            mResult = self.mClient.files.remove({'_id':id})
            print "Deleted in Mongo"
            success = True
        except:
            print "Can't delete in Mongo"
            success = False

        return success and self.rClient.delete(id)

#    def store_replicated_data(self, id, data):
#        self.replicationClient.set(id, data)
#        return True

    # Get data from Redis. If not available, get from Mongo and update Redis
    def get_data(self, id):
        data = self.rClient.get(id)
        print "Redis has it " + data

        if None:
            data = self.mClient.files.find({'_id':id},{'data':1})
            self.rClient.set(id, data)
            print "Only Mongo has it " + data

#        if DEBUG:
#            print "Inside get data. Data is : {}".format(id)
        return data