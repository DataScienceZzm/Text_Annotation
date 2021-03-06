import numpy as np
import tensorflow as tf
from ..net import model_crf, model_softmax


def train_annotation(x=None,
                     y=None,
                     model='crf',
                     num_words=5000,
                     num_units=128,
                     num_layers=2,
                     num_tags=5,
                     max_seq_len=20,
                     batchsize=64,
                     epoch=1,
                     model_path=None):
    input_data = tf.placeholder(tf.int32, [None, None])
    output_targets = tf.placeholder(tf.int32, [None, None])

    if model == 'crf':
        tensors = model_crf(input_data=input_data,
                            output_targets=output_targets,
                            num_words=num_words,
                            num_units=num_units,
                            num_layers=num_layers,
                            batchsize=batchsize,
                            num_tags=num_tags,
                            max_seq_len=max_seq_len,
                            train=True)
    elif model == 'softmax':
        tensors = model_softmax(input_data=input_data,
                                output_targets=output_targets,
                                num_words=num_words,
                                num_units=num_units,
                                num_layers=num_layers,
                                batchsize=batchsize,
                                num_tags=num_tags,
                                train=True)

    saver = tf.train.Saver(tf.global_variables(), max_to_keep=20)
    initializer = tf.global_variables_initializer()
    print('start training')

    with tf.Session() as sess:
        sess.run(initializer)
        index_all = np.arange(len(x))

        for epoch in range(epoch):
            for batch in range(len(x) // batchsize * 1):
                index_batch = np.random.choice(index_all, batchsize)

                x_batch = x[index_batch]
                y_batch = y[index_batch]

                print(x_batch.shape)
                loss, accu, _ = sess.run([
                    tensors['loss'],
                    tensors['accu'],
                    tensors['train_op']
                ], feed_dict={input_data: x_batch, output_targets: y_batch})
                print('Epoch: %d, batch: %d, loss: %.6f, accu: %.6f' %
                      (epoch + 1, batch + 1, loss, accu))
            saver.save(sess, model_path, global_step=epoch)
