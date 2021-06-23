import tensorflow as tf

with tf.device('/cpu:0'):
    a_c = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[2, 3], name='a-cpu')
    b_c = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[3, 2], name='b-cpu')
    c_c = tf.matmul(a_c, b_c, name='c-cpu')

with tf.device('/gpu:0'):
    a_g = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[2, 3], name='a-gpu')
    b_g = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[3, 2], name='b-gpu')
    c_g = tf.matmul(a_g, b_g, name='c-gpu')

with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
    print (sess.run(c_c))
    print (sess.run(c_g))

quit()
