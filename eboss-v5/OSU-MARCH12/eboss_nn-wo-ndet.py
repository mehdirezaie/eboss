
import tensorflow as tf
import numpy as np
import os

class Netregression(object):
    """
        class for a general regression
    """
    def __init__(self, Traind, Testd):
        # reading data
        # train
        trainX = Traind['features']
        trainY = Traind['label'].astype("f8")
        trainhpix = Traind['hpix']
        # test
        testX  = Testd['features']
        testY  = Testd['label'].astype("f8")
        testhpix = Testd['hpix']
        #
        #        
        # add extra dimension on x
        if len(trainX.shape) == 1:
            trainX = trainX[:, np.newaxis]
            testX  = testX[:, np.newaxis]
            self.feature = 1
        if len(trainX.shape) == 2:
            self.feature = trainX.shape[1]
        self.traindata = (trainhpix, trainX, trainY[:,np.newaxis])
        self.testdata  = (testhpix, testX, testY[:,np.newaxis])
        
    def train_evaluate(self, learning_rate=0.001,
                       batchsize=100, nepoch=10, nchain=5,
                      Units=(10,10)):
        #
        nfeature = self.feature #
        nclass   = 1 # 0 or 1
        #
        x   = tf.placeholder(tf.float32, [None, nfeature])
        y0  = tf.layers.dense(x, units=Units[0], activation=tf.nn.relu)
        y1  = tf.layers.dense(y0, units=Units[1], activation=tf.nn.relu)
        y   = tf.layers.dense(y1, units=nclass, activation=None)
        y_  = tf.placeholder(tf.float32, [None, nclass])
        mse = tf.losses.mean_squared_error(y_, y)
        
        global_step = tf.Variable(0, name='global_step', trainable=False)
        optimizer   = tf.train.AdamOptimizer(learning_rate)
        train_step  = optimizer.minimize(mse, global_step=global_step)
        
        
        _,train_Xs, train_Ys       = self.traindata
        test_hpix,test_Xs, test_Ys = self.testdata    
        train_size               = train_Xs.shape[0]
        #
        # using training label/feature mean and std
        # to normalize training/testing label/feature
        meanX = np.mean(train_Xs, axis=0)
        stdX  = np.std(train_Xs, axis=0)
        meanY = np.mean(train_Ys, axis=0)
        stdY  = np.std(train_Ys, axis=0)
        self.Xstat = (meanX, stdX)
        self.Ystat = (meanY, stdY)
        
        train_X = (train_Xs - meanX) / stdX
        train_Y = (train_Ys - meanY) / stdY
        test_X  = (test_Xs - meanX) / stdX
        test_Y  = (test_Ys - meanY) / stdY
        
        # baseline rmse
        baselineY  = np.mean(train_Y)
        assert np.abs(baselineY) < 1.e-6, "check normalization!"
        baseline_testrmse  = np.sqrt(np.mean((test_Y)**2))
        baseline_trainrmse  = np.sqrt(np.mean((train_Y)**2))
        
        
        if np.mod(train_size, batchsize) == 0:
            nep = (train_size // batchsize)
        else:
            nep = (train_size // batchsize) + 1

        self.epoch_RMSEs = []
        self.chain_y     = []
        for ii in range(nchain):
            print('chain ',ii)
            #
            i_list    = []
            e_list    = []
            rmse_list = []
            #
            #sess = tf.Session(config=tf.ConfigProto(inter_op_parallelism_threads=int(os.environ['NUM_INTER_THREADS']),
            #                            intra_op_parallelism_threads=int(os.environ['NUM_INTRA_THREADS'])))
            sess = tf.InteractiveSession()
            tf.global_variables_initializer().run()            
            for i in range(nepoch):
                #
                for k in range(nep):
                    j = k*batchsize
                    if j+batchsize > train_size:
                        batch_xs, batch_ys = train_X[j:-1], train_Y[j:-1]
                    else:
                        batch_xs, batch_ys = train_X[j:j+batchsize], train_Y[j:j+batchsize]
                    sess.run(train_step, feed_dict={x: batch_xs, y_:batch_ys}) 
                #
                train_loss = mse.eval(feed_dict={x:train_X, y_:train_Y})
                test_loss  = mse.eval(feed_dict={x:test_X, y_: test_Y})
                rmse_list.append([i, np.sqrt(train_loss), np.sqrt(test_loss)])
            #
            y_mse, y_pred  = sess.run((mse,y),feed_dict={x: test_X, y_: test_Y})
            #
            self.chain_y.append([ii, y_pred])
            self.epoch_RMSEs.append([ii, np.sqrt(y_mse), np.array(rmse_list)])
            
        self.optionsdic = {}
        self.optionsdic["baselineRMSE"]  = (baseline_trainrmse,baseline_testrmse)
        self.optionsdic['learning_rate'] = learning_rate
        self.optionsdic['batchsize']     = batchsize
        self.optionsdic['nepoch']        = nepoch
        self.optionsdic['nchain']        = nchain
        self.optionsdic['Units']         = Units
        self.optionsdic['stats']         = {"xstat":self.Xstat, "ystat":self.Ystat}
            
            
    def savez(self, indir='./', name='regression_2hl_5chain_10epoch'):
        output = {}
        output['train']       = self.traindata
        output['test']        = self.testdata
        output['epoch_RMSEs'] = self.epoch_RMSEs
        output['chain_y']     = self.chain_y
        output['options']     = self.optionsdic
        if indir[-1] != '/':
            indir += '/'
        if not os.path.exists(indir):
            os.makedirs(indir)
        if not os.path.isfile(indir+name+'.npz'):
            np.savez(indir+name, output)
        else:
            print("there is already a file!")
            name = name+''.join(time.asctime().split(' '))
            np.savez(indir+name, output)
        print('output is saved as {} under {}'.format(name, indir))

def run_nchainlearning(indir, *arrays, **options):
    n_arrays = len(arrays)
    if n_arrays != 2:
        raise ValueError("Two arrays for train and test are required")
    net = Netregression(*arrays)
    net.train_evaluate(**options) #learning_rate=0.01, batchsize=100, nepoch=10, nchain=5
    #
    batchsize = options.pop('batchsize', 100)
    nepoch = options.pop('nepoch', 10)
    nchain = options.pop('nchain', 5)
    Units  = options.pop('Units', (10,10))
    Lrate  = options.pop('learning_rate', 0.001)
    units  = str(Units[0])+str(Units[1])
    ouname = 'reg-nepoch'+str(nepoch)+'-nchain'+str(nchain)
    ouname += '-batchsize'+str(batchsize)+'units'+units
    ouname += '-Lrate'+str(Lrate)
    #
    net.savez(indir=indir, name=ouname)        
        
# read data
path3 = '/global/cscratch1/sd/mehdi/eboss/ebossv5_10_7/march12/data4fold/'
data_eboss =np.load(path3+'test_train_eboss_4fold-wo-ndet.npy').item()



#
config = {'nchain':10, 'nepoch':500, 'batchsize':2000, 'Units':(10,10), 'learning_rate':.01}
for i in range(4): # 4 fold
    fold = 'fold'+str(i)
    print(fold, ' is being processed')
    run_nchainlearning(path3+'wo-ndet/'+fold+'/',
                   data_eboss['train'][fold], 
                   data_eboss['test'][fold],
                  **config)
