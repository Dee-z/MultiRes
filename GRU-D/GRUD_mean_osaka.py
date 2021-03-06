#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tqdm
import torch
import numpy as np
import pandas as pd
import os
import math
import warnings
import itertools
import numbers
import torch.utils.data as utils
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score, precision_recall_fscore_support


# functions to process the time in the data
def timeparser(time):
    return pd.to_timedelta(time + ':00')


def timedelta_to_day_figure(timedelta):
    return timedelta.days + (timedelta.seconds / 86400)  # (24*60*60)


def normalization(desc, inputs):
    # for each catagory
    for i in range(desc.shape[0]):
        # for each value
        for j in range(len(inputs[i])):
            inputs[i][j] = (inputs[i][j] - desc[i][3]) / desc[i][5]
    return inputs


# In[22]:

# print('Dataframe to dataset....')
'''
dataframe to dataset
'''


def df_to_x_m_d(df, dfm, inputdict, size, id_posistion, split, features_list):
    grouped_data = df.groupby('Time')

    # generate input vectors
    x = np.zeros((len(inputdict), grouped_data.ngroups))

    # print("X Shape", x.shape)
    masking = np.zeros((len(inputdict), grouped_data.ngroups))
    # print("Masking Shape", masking.shape)
    delta = np.zeros((split, size))
    # print('Delta shape ', delta.shape)
    timetable = np.zeros(grouped_data.ngroups)
    id = 0

    all_x = np.zeros((split, 1))

    s_dataset = np.zeros((3, split, size))

    if grouped_data.ngroups > size:

        # fill the x and masking vectors
        pre_time = pd.to_timedelta(0)
        t = 0
        for row_index, value in df.iterrows():
            #     '''
            #     t = colum, time frame
            #     agg_no = row, variable
            #     '''
            # print(value)
            # agg_no = inputdict[value.Parameter]

            # same timeline check.
            if pre_time != value.Time:
                pre_time = value.Time
                timetable[t] = value.Time
                t += 1

            # print('agg_no : {}\t t : {}\t value : {}'.format(agg_no, t, value.Value))
            # x[agg_no, t] = value.Value
            # masking[agg_no, t] = 1

        x = df.as_matrix(columns=features_list).T
        masking = dfm.as_matrix(columns=features_list).T
        # print(x.shape, masking.shape)

        # print(x.shape)
        # generate index that has most parameters and first/last one.
        ran_index = grouped_data.count()
        ran_index = ran_index.reset_index()
        # ran_index = ran_index.sort_values('Value', ascending=False)
        ran_index = ran_index[:size]
        ran_index = ran_index.sort_index()
        ran_index = np.asarray(ran_index.index.values)
        ran_index[0] = 0
        ran_index[size - 1] = grouped_data.ngroups - 1

        # print(ran_index)

        # take id for outcome comparing
        # id = x[id_posistion, 0]

        # remove unnesserly parts(rows)
        x = x[:split, :]
        masking = masking[:split, :]

        # coulme(time) sampling
        x_sample = np.zeros((split, size))
        m_sample = np.zeros((split, size))
        time_sample = np.zeros(size)

        t_x_sample = x_sample.T
        t_marsking = m_sample.T
        # t_time = t_sample.T

        t_x = x.T
        t_m = masking.T
        # t_t = t.T

        it = np.nditer(ran_index, flags=['f_index'])
        while not it.finished:
            # print('it.index = {}, it[0] = {}, ran_index = {}'.format(it.index, it[0], ran_index[it.index]))
            t_x_sample[it.index] = t_x[it[0]]
            t_marsking[it.index] = t_m[it[0]]
            time_sample[it.index] = timetable[it[0]]
            it.iternext()

        x = x_sample
        masking = m_sample
        timetable = time_sample
        '''
        # normalize the X
        nor_x = x/max_input[:, np.newaxis]
        '''
        # fill the delta vectors
        for index, value in np.ndenumerate(masking):
            '''
            index[0] = row, agg
            index[1] = col, time
            '''
            if index[1] == 0:
                delta[index[0], index[1]] = 0
            elif masking[index[0], index[1] - 1] == 0:
                delta[index[0], index[1]] = timetable[index[1]] - timetable[index[1] - 1] + delta[
                    index[0], index[1] - 1]
            else:
                delta[index[0], index[1]] = timetable[index[1]] - timetable[index[1] - 1]

    else:

        # fill the x and masking vectors
        pre_time = pd.to_timedelta(0)
        t = 0
        for row_index, value in df.iterrows():
            '''
            t = colum, time frame
            agg_no = row, variable
            '''
            # print(value)
            # agg_no = inputdict[value.Parameter]

            # same timeline check.        
            if pre_time != value.Time:
                pre_time = value.Time
                timetable[t] = value.Time
                t += 1

            # print('agg_no : {}\t t : {}\t value : {}'.format(agg_no, t, value.Value))
            # x[agg_no, t] = value.Value
            # masking[agg_no, t] = 1

        # take id for outcome comparing
        x = df.as_matrix(columns=features_list).T
        masking = dfm.as_matrix(columns=features_list).T
        # print(x.shape, masking.shape)

        # id = x[id_posistion, 0]

        # remove unnesserly parts(rows)
        x = x[:split, :]
        masking = masking[:split, :]

        x = np.pad(x, ((0, 0), (size - grouped_data.ngroups, 0)), 'constant')
        masking = np.pad(masking, ((0, 0), (size - grouped_data.ngroups, 0)), 'constant')
        timetable = np.pad(timetable, (size - grouped_data.ngroups, 0), 'constant')
        '''
        # normalize the X
        nor_x = x/max_input[:, np.newaxis]
        '''
        # fill the delta vectors
        for index, value in np.ndenumerate(masking):
            '''
            index[0] = row, agg
            index[1] = col, time
            '''
            if index[1] == 0:
                delta[index[0], index[1]] = 0
            elif masking[index[0], index[1] - 1] == 0:
                delta[index[0], index[1]] = timetable[index[1]] - timetable[index[1] - 1] + delta[
                    index[0], index[1] - 1]
            else:
                delta[index[0], index[1]] = timetable[index[1]] - timetable[index[1] - 1]

    all_x = np.concatenate((all_x, x), axis=1)
    all_x = all_x[:, 1:]

    s_dataset[0] = x
    s_dataset[1] = masking
    s_dataset[2] = delta

    return s_dataset, all_x, id


# In[23]:
#
inputdict = {
    "A": 0,  # o
    "B": 1,  # o
    "C": 2,  # o
    "D": 3,  # o
    "E": 4,  # o
    "F": 5,  # o
    "G": 6,  # o
    "H": 7,  # o
    "I": 8,  # o
    "J": 9,  # o
    "K": 10,  # o
    "L": 11,  # o
    "M": 12,  # o
    "N": 13,  # o
    "O": 14,  # o
    "P": 15,  # o
    "Q": 16,  # o
    "R": 17,  # o
    "S": 18,  # o
    "T": 19,  # o
    "U": 20,
}

# def df_to_x_m_d(df, inputdict, mean, std, size, id_posistion, split):
size = 500  # steps ~ from the paper
id_posistion = 37
input_length = 21  # Number of features
# print(d)
# print(len(df['T0_ID271435_Walk1.csv'][0]))
# print(len(d['train_ids'])+len(d['val_ids'])+len(d['test_ids']))
# for id in d['train_ids']:
#     x = np.asarray(df[id][0])
#     print(x.shape)
dataset = np.zeros((1, 3, input_length, size))

all_x_add = np.zeros((input_length, 1))

label_dict = {'SlopeDown.csv': '0', 'SlopeUp.csv': '1', 'Walk1.csv': '2', 'Walk2.csv': '2'}
q = 0
d = pd.read_pickle('Data/final_osaka_data_avg_60_flags.pkl')
# print(d.keys())
df = pd.DataFrame.from_dict(d['data'])
# print(df)
osaka_outcomes = []
order = ['train_ids', 'val_ids', 'test_ids']
features_list = sorted(inputdict.keys())
for o in order:
    for id in tqdm.tqdm(d[o]):
        osaka_outcomes.append(label_dict[df[id][2]])

        marray = 1 - np.asarray(df[id][1])[:, 3:]
        xarray = np.multiply(np.asarray(df[id][0])[:, 3:], marray)
        df_subject = pd.DataFrame(xarray, columns=features_list)
        df_masking = pd.DataFrame(marray, columns=features_list)
        n_rows = len(df_subject['A'])
        df_subject['Time'] = pd.Series(np.arange(n_rows), index=df_subject.index)
        # print(df_subject)
        s_dataset, all_x, _ = df_to_x_m_d(df=df_subject, dfm=df_masking, inputdict=inputdict, size=size,
                                          id_posistion=id_posistion,
                                          split=input_length, features_list=features_list)

        dataset = np.concatenate((dataset, s_dataset[np.newaxis, :, :, :]))
        all_x_add = np.concatenate((all_x_add, all_x), axis=1)

print(len(osaka_outcomes))

dataset = dataset[1:, :, :, :]
# (total datasets, kind of data(x, masking, and delta), input length, num of varience)
# (4000, 3, 33, 49)
print(dataset.shape)
print(dataset[0].shape)
print(dataset[0][0][0])
print(all_x_add.shape)
all_x_add = all_x_add[:, 1:]
print(all_x_add.shape)


# In[24]:

trp = 0.64

def get_mean(x):
    x_mean = []
    l = int(trp*x.shape[1])
    for i in range(x.shape[0]):
        mean = np.mean(x[i][:l])
        x_mean.append(mean)
    return x_mean


# In[25]:


def get_median(x):
    x_median = []
    l = int(trp*x.shape[1])
    for i in range(x.shape[0]):
        median = np.median(x[i][:l])
        x_median.append(median)
    return x_median


# In[26]:


def get_std(x):
    x_std = []
    l = int(trp*x.shape[1])
    for i in range(x.shape[0]):
        std = np.std(x[i][:l])
        x_std.append(std)
    return x_std


# In[27]:


def get_var(x):
    x_var = []
    l = int(trp*x.shape[1])
    for i in range(x.shape[0]):
        var = np.var(x[i][:l])
        x_var.append(var)
    return x_var


# In[28]:


x_mean = get_mean(all_x_add)
print(x_mean)
print(len(x_mean))

# In[29]:


x_std = get_std(all_x_add)
print(x_std)
print(len(x_std))


# In[30]:


# dataset shape : (4000, 3, 33, 49)
def dataset_normalize(dataset, mean, std):
    for i in range(dataset.shape[0]):
        dataset[i][0] = (dataset[i][0] - mean[:, None])
        dataset[i][0] = dataset[i][0] / std[:, None]

    return dataset


# In[31]:


x_mean = np.asarray(x_mean)
x_std = np.asarray(x_std)

# In[32]:

print('Normalizing dataset...')
dataset = dataset_normalize(dataset=dataset, mean=x_mean, std=x_std)
print(dataset[0][0][0])


# In[33]:


def normalize_chk(dataset):
    all_x_add = np.zeros((dataset[0][0].shape[0], 1))
    for i in range(dataset.shape[0]):
        all_x_add = np.concatenate((all_x_add, dataset[i][0]), axis=1)

    mean = get_mean(all_x_add)
    median = get_median(all_x_add)
    std = get_std(all_x_add)
    var = get_var(all_x_add)

    print('mean')
    print(mean)
    print('median')
    print(median)
    print('std')
    print(std)
    print('var')
    print(var)

    return mean, median, std, var


# In[34]:


nor_mean, nor_median, nor_std, nor_var = normalize_chk(dataset)

# In[35]:

print('Saving new dataset....')
np.save('./input/x_mean_osaka_1185', nor_mean)
np.save('./input/x_median_osaka_1185', nor_median)
np.save('./input/dataset_osaka_1185', dataset)
np.save('./input/outcomes_osaka_1185', osaka_outcomes)


# print('Loading new dataset 36......')
# t_dataset = np.load('./input/dataset.npy')

# print(t_dataset.shape)


# define model
class GRUD(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, x_mean=0, bias=True, batch_first=False,
                 bidirectional=False, dropout_type='mloss', dropout=0):
        super(GRUD, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.zeros = torch.autograd.Variable(torch.zeros(input_size))
        self.x_mean = torch.autograd.Variable(torch.tensor(x_mean))
        self.bias = bias
        self.batch_first = batch_first
        self.dropout_type = dropout_type
        self.dropout = dropout
        self.bidirectional = bidirectional
        num_directions = 2 if bidirectional else 1

        if not isinstance(dropout, numbers.Number) or not 0 <= dropout <= 1 or isinstance(dropout, bool):
            raise ValueError("dropout should be a number in range [0, 1] "
                             "representing the probability of an element being "
                             "zeroed")
        if dropout > 0 and num_layers == 1:
            warnings.warn("dropout option adds dropout after all but last "
                          "recurrent layer, so non-zero dropout expects "
                          "num_layers greater than 1, but got dropout={} and "
                          "num_layers={}".format(dropout, num_layers))

        ################################
        gate_size = 1  # not used
        ################################

        self._all_weights = []

        '''
        w_ih = Parameter(torch.Tensor(gate_size, layer_input_size))
        w_hh = Parameter(torch.Tensor(gate_size, hidden_size))
        b_ih = Parameter(torch.Tensor(gate_size))
        b_hh = Parameter(torch.Tensor(gate_size))
        layer_params = (w_ih, w_hh, b_ih, b_hh)
        '''
        # decay rates gamma
        w_dg_x = torch.nn.Parameter(torch.Tensor(input_size))
        w_dg_h = torch.nn.Parameter(torch.Tensor(hidden_size))

        # z
        w_xz = torch.nn.Parameter(torch.Tensor(input_size))
        w_hz = torch.nn.Parameter(torch.Tensor(hidden_size))
        w_mz = torch.nn.Parameter(torch.Tensor(input_size))

        # r
        w_xr = torch.nn.Parameter(torch.Tensor(input_size))
        w_hr = torch.nn.Parameter(torch.Tensor(hidden_size))
        w_mr = torch.nn.Parameter(torch.Tensor(input_size))

        # h_tilde
        w_xh = torch.nn.Parameter(torch.Tensor(input_size))
        w_hh = torch.nn.Parameter(torch.Tensor(hidden_size))
        w_mh = torch.nn.Parameter(torch.Tensor(input_size))

        # y (output)
        w_hy = torch.nn.Parameter(torch.Tensor(output_size, hidden_size))

        # bias
        b_dg_x = torch.nn.Parameter(torch.Tensor(hidden_size))
        b_dg_h = torch.nn.Parameter(torch.Tensor(hidden_size))
        b_z = torch.nn.Parameter(torch.Tensor(hidden_size))
        b_r = torch.nn.Parameter(torch.Tensor(hidden_size))
        b_h = torch.nn.Parameter(torch.Tensor(hidden_size))
        b_y = torch.nn.Parameter(torch.Tensor(output_size))

        layer_params = (
            w_dg_x, w_dg_h, w_xz, w_hz, w_mz, w_xr, w_hr, w_mr, w_xh, w_hh, w_mh, w_hy, b_dg_x, b_dg_h, b_z, b_r, b_h,
            b_y)

        param_names = ['weight_dg_x', 'weight_dg_h', 'weight_xz', 'weight_hz', 'weight_mz', 'weight_xr', 'weight_hr',
                       'weight_mr', 'weight_xh', 'weight_hh', 'weight_mh', 'weight_hy']
        if bias:
            param_names += ['bias_dg_x', 'bias_dg_h', 'bias_z', 'bias_r', 'bias_h', 'bias_y']

        for name, param in zip(param_names, layer_params):
            setattr(self, name, param)
        self._all_weights.append(param_names)

        self.flatten_parameters()
        self.reset_parameters()

    def flatten_parameters(self):
        """
        Resets parameter data pointer so that they can use faster code paths.
        Right now, this works only if the module is on the GPU and cuDNN is enabled.
        Otherwise, it's a no-op.
        """
        any_param = next(self.parameters()).data
        if not any_param.is_cuda or not torch.backends.cudnn.is_acceptable(any_param):
            return

        # If any parameters alias, we fall back to the slower, copying code path. This is
        # a sufficient check, because overlapping parameter buffers that don't completely
        # alias would break the assumptions of the uniqueness check in
        # Module.named_parameters().
        all_weights = self._flat_weights
        unique_data_ptrs = set(p.data_ptr() for p in all_weights)
        if len(unique_data_ptrs) != len(all_weights):
            return

        with torch.cuda.device_of(any_param):
            import torch.backends.cudnn.rnn as rnn

            # NB: This is a temporary hack while we still don't have Tensor
            # bindings for ATen functions
            with torch.no_grad():
                # NB: this is an INPLACE function on all_weights, that's why the
                # no_grad() is necessary.
                torch._cudnn_rnn_flatten_weight(
                    all_weights, (4 if self.bias else 2),
                    self.input_size, rnn.get_cudnn_mode(self.mode), self.hidden_size, self.num_layers,
                    self.batch_first, bool(self.bidirectional))

    def _apply(self, fn):
        ret = super(GRUD, self)._apply(fn)
        self.flatten_parameters()
        return ret

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.hidden_size)
        for weight in self.parameters():
            torch.nn.init.uniform_(weight, -stdv, stdv)

    def check_forward_args(self, input, hidden, batch_sizes):
        is_input_packed = batch_sizes is not None
        expected_input_dim = 2 if is_input_packed else 3
        if input.dim() != expected_input_dim:
            raise RuntimeError(
                'input must have {} dimensions, got {}'.format(
                    expected_input_dim, input.dim()))
        if self.input_size != input.size(-1):
            raise RuntimeError(
                'input.size(-1) must be equal to input_size. Expected {}, got {}'.format(
                    self.input_size, input.size(-1)))

        if is_input_packed:
            mini_batch = int(batch_sizes[0])
        else:
            mini_batch = input.size(0) if self.batch_first else input.size(1)

        num_directions = 2 if self.bidirectional else 1
        expected_hidden_size = (self.num_layers * num_directions,
                                mini_batch, self.hidden_size)

        def check_hidden_size(hx, expected_hidden_size, msg='Expected hidden size {}, got {}'):
            if tuple(hx.size()) != expected_hidden_size:
                raise RuntimeError(msg.format(expected_hidden_size, tuple(hx.size())))

        if self.mode == 'LSTM':
            check_hidden_size(hidden[0], expected_hidden_size,
                              'Expected hidden[0] size {}, got {}')
            check_hidden_size(hidden[1], expected_hidden_size,
                              'Expected hidden[1] size {}, got {}')
        else:
            check_hidden_size(hidden, expected_hidden_size)

    def extra_repr(self):
        s = '{input_size}, {hidden_size}'
        if self.num_layers != 1:
            s += ', num_layers={num_layers}'
        if self.bias is not True:
            s += ', bias={bias}'
        if self.batch_first is not False:
            s += ', batch_first={batch_first}'
        if self.dropout != 0:
            s += ', dropout={dropout}'
        if self.bidirectional is not False:
            s += ', bidirectional={bidirectional}'
        return s.format(**self.__dict__)

    def __setstate__(self, d):
        super(GRUD, self).__setstate__(d)
        if 'all_weights' in d:
            self._all_weights = d['all_weights']
        if isinstance(self._all_weights[0][0], str):
            return
        num_layers = self.num_layers
        num_directions = 2 if self.bidirectional else 1
        self._all_weights = []

        weights = ['weight_dg_x', 'weight_dg_h', 'weight_xz', 'weight_hz', 'weight_mz', 'weight_xr', 'weight_hr',
                   'weight_mr', 'weight_xh', 'weight_hh', 'weight_mh', 'weight_hy', 'bias_dg_x', 'bias_dg_h', 'bias_z',
                   'bias_r', 'bias_h', 'bias_y']

        if self.bias:
            self._all_weights += [weights]
        else:
            self._all_weights += [weights[:2]]

    @property
    def _flat_weights(self):
        return list(self._parameters.values())

    @property
    def all_weights(self):
        return [[getattr(self, weight) for weight in weights] for weights in self._all_weights]

    def forward(self, input):
        # input.size = (3, 33,49) : num_input or num_hidden, num_layer or step
        X = torch.squeeze(input[0])  # .size = (33,49)
        Mask = torch.squeeze(input[1])  # .size = (33,49)
        Delta = torch.squeeze(input[2])  # .size = (33,49)
        Hidden_State = torch.autograd.Variable(torch.zeros(input_size))

        step_size = X.size(1)  # 49
        # print('step size : ', step_size)

        output = None
        h = Hidden_State

        # decay rates gamma
        w_dg_x = getattr(self, 'weight_dg_x')
        w_dg_h = getattr(self, 'weight_dg_h')

        # z
        w_xz = getattr(self, 'weight_xz')
        w_hz = getattr(self, 'weight_hz')
        w_mz = getattr(self, 'weight_mz')

        # r
        w_xr = getattr(self, 'weight_xr')
        w_hr = getattr(self, 'weight_hr')
        w_mr = getattr(self, 'weight_mr')

        # h_tilde
        w_xh = getattr(self, 'weight_xh')
        w_hh = getattr(self, 'weight_hh')
        w_mh = getattr(self, 'weight_mh')

        # bias
        b_dg_x = getattr(self, 'bias_dg_x')
        b_dg_h = getattr(self, 'bias_dg_h')
        b_z = getattr(self, 'bias_z')
        b_r = getattr(self, 'bias_r')
        b_h = getattr(self, 'bias_h')

        for layer in range(num_layers):

            x = torch.squeeze(X[:, layer:layer + 1])
            m = torch.squeeze(Mask[:, layer:layer + 1])
            d = torch.squeeze(Delta[:, layer:layer + 1])

            # (4)
            gamma_x = torch.exp(-torch.max(self.zeros, (w_dg_x * d + b_dg_x)))
            gamma_h = torch.exp(-torch.max(self.zeros, (w_dg_h * d + b_dg_h)))

            # (5)
            x = m * x + (1 - m) * (gamma_x * x + (1 - gamma_x) * self.x_mean)

            # (6)
            if self.dropout == 0:
                h = gamma_h * h

                z = torch.sigmoid((w_xz * x + w_hz * h + w_mz * m + b_z))
                r = torch.sigmoid((w_xr * x + w_hr * h + w_mr * m + b_r))
                h_tilde = torch.tanh((w_xh * x + w_hh * (r * h) + w_mh * m + b_h))

                h = (1 - z) * h + z * h_tilde

            elif self.dropout_type == 'Moon':
                '''
                RNNDROP: a novel dropout for rnn in asr(2015)
                '''
                h = gamma_h * h

                z = torch.sigmoid((w_xz * x + w_hz * h + w_mz * m + b_z))
                r = torch.sigmoid((w_xr * x + w_hr * h + w_mr * m + b_r))

                h_tilde = torch.tanh((w_xh * x + w_hh * (r * h) + w_mh * m + b_h))

                h = (1 - z) * h + z * h_tilde
                dropout = torch.nn.Dropout(p=self.dropout)
                h = dropout(h)

            elif self.dropout_type == 'Gal':
                '''
                A Theoretically grounded application of dropout in recurrent neural networks(2015)
                '''
                dropout = torch.nn.Dropout(p=self.dropout)
                h = dropout(h)

                h = gamma_h * h

                z = torch.sigmoid((w_xz * x + w_hz * h + w_mz * m + b_z))
                r = torch.sigmoid((w_xr * x + w_hr * h + w_mr * m + b_r))
                h_tilde = torch.tanh((w_xh * x + w_hh * (r * h) + w_mh * m + b_h))

                h = (1 - z) * h + z * h_tilde

            elif self.dropout_type == 'mloss':
                '''
                recurrent dropout without memory loss arXiv 1603.05118
                g = h_tilde, p = the probability to not drop a neuron
                '''

                h = gamma_h * h

                z = torch.sigmoid((w_xz * x + w_hz * h + w_mz * m + b_z))
                r = torch.sigmoid((w_xr * x + w_hr * h + w_mr * m + b_r))
                h_tilde = torch.tanh((w_xh * x + w_hh * (r * h) + w_mh * m + b_h))

                dropout = torch.nn.Dropout(p=self.dropout)
                h_tilde = dropout(h_tilde)

                h = (1 - z) * h + z * h_tilde

            else:
                h = gamma_h * h

                z = torch.sigmoid((w_xz * x + w_hz * h + w_mz * m + b_z))
                r = torch.sigmoid((w_xr * x + w_hr * h + w_mr * m + b_r))
                h_tilde = torch.tanh((w_xh * x + w_hh * (r * h) + w_mh * m + b_h))

                h = (1 - z) * h + z * h_tilde

        w_hy = getattr(self, 'weight_hy')
        b_y = getattr(self, 'bias_y')

        output = torch.matmul(w_hy, h) + b_y
        output = torch.sigmoid(output)

        return output


# In[5]:


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# In[6]:


def data_dataloader(dataset, outcomes, train_proportion=0.64, dev_proportion=0.16, test_proportion=0.2):
    train_index = int(np.floor(dataset.shape[0] * train_proportion))
    dev_index = int(np.floor(dataset.shape[0] * (train_proportion + dev_proportion)))

    # split dataset to tarin/dev/test set
    train_data, train_label = dataset[:train_index, :, :, :], outcomes[:train_index, :]
    dev_data, dev_label = dataset[train_index:dev_index, :, :, :], outcomes[train_index:dev_index, :]
    test_data, test_label = dataset[dev_index:, :, :, :], outcomes[dev_index:, :]

    # ndarray to tensor
    train_data, train_label = torch.Tensor(train_data), torch.Tensor(train_label.astype(int))
    dev_data, dev_label = torch.Tensor(dev_data), torch.Tensor(dev_label.astype(int))
    test_data, test_label = torch.Tensor(test_data), torch.Tensor(test_label.astype(int))

    # tensor to dataset
    train_dataset = utils.TensorDataset(train_data, train_label)
    dev_dataset = utils.TensorDataset(dev_data, dev_label)
    test_dataset = utils.TensorDataset(test_data, test_label)

    # dataset to dataloader 
    train_dataloader = utils.DataLoader(train_dataset)
    dev_dataloader = utils.DataLoader(dev_dataset)
    test_dataloader = utils.DataLoader(test_dataset)

    print("train_data.shape : {}\t train_label.shape : {}".format(train_data.shape, train_label.shape))
    print("dev_data.shape : {}\t dev_label.shape : {}".format(dev_data.shape, dev_label.shape))
    print("test_data.shape : {}\t test_label.shape : {}".format(test_data.shape, test_label.shape))

    return train_dataloader, dev_dataloader, test_dataloader


# In[7]:


t_dataset = np.load('./input/dataset_osaka_1185.npy')
osaka_outcomes = np.load('./input/outcomes_osaka_1185.npy')
# t_dataset_old = np.load('./input/dataset.npy')
# print(t_dataset_old[0][0][0])
# t_out = np.load('./input/y1_out.npy')
# outcomes_oursplit = []
# with open('outcomes.txt', 'r') as f:
#     for line in f:
#         line = line.rstrip('\n')
#         outcomes_oursplit.append(int(line))
# print(outcomes_oursplit)
# t_out = np.asarray(outcomes_oursplit)
# t_out.resize((4000, 1))
# t_out = np.load('./input/survival_out.npy')
t_out = np.asarray(osaka_outcomes)
t_out.resize((1616, 1))
print(t_dataset[0][0][0])
print(t_out[0])
print(t_dataset.shape)
print(len(t_out))

train_dataloader, dev_dataloader, test_dataloader = data_dataloader(t_dataset, t_out)

# In[8]:


'''
in the paper : 49 layers, 33 input, 18838 parameters
input : 10-weights(*input), 6 - biases
Y: 1 weight(hidden*output), 1 bias(output)
Input : hidden : output : layer  = # of parameters : len(para)
1:1:1:1 = 18 : 18
2:1:1:1 = 25 : 18  // +7 as expected
1:1:1:2 = 34 : 18 // 34 = 16*2 + 2
33:33:1:1 = 562 : 18 // 16*33(528) + 33*1 +1 = 562
33:33:5:1 = 698 : 18 // 16*33(528) + 33*5(165) +5 = 698
33:33:5:49 = 26042 : 18 // 16*33*49(25872) + 33*5(165) +5 = 698
weights = 10*33*49(16170) + 33*5(165) = 16335 gap : 2503

'''


# In[8]:


def fit(model, criterion, learning_rate, train_dataloader, dev_dataloader, test_dataloader, learning_rate_decay=0,
        n_epochs=30):
    epoch_losses = []

    # to check the update 
    old_state_dict = {}
    for key in model.state_dict():
        old_state_dict[key] = model.state_dict()[key].clone()

    graph_epochs = []
    fscores_train = []
    fscores_val = []
    fscores_test = []
    for epoch in range(n_epochs):

        if learning_rate_decay != 0:

            # every [decay_step] epoch reduce the learning rate by half
            if epoch % learning_rate_decay == 0:
                learning_rate = learning_rate / 2
                optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
                print('at epoch {} learning_rate is updated to {}'.format(epoch, learning_rate))
        else:
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # train the model
        losses, acc = [], []
        label, pred = [], []
        y_pred_col = []
        model.train()
        q = 0
        for train_data, train_label in train_dataloader:
            # Zero the parameter gradients
            optimizer.zero_grad()
            q += 1
            if q % 100 == 0:
                print(q)
            # Squeeze the data [1, 33, 49], [1,5] to [33, 49], [5]
            train_data = torch.squeeze(train_data)
            train_label = torch.squeeze(train_label)

            # Forward pass : Compute predicted y by passing train data to the model
            y_pred = model(train_data)

            # y_pred = y_pred[:, None]
            # train_label = train_label[:, None]

            # print(y_pred.shape)
            # print(train_label.shape)

            # Save predict and label
            # y_pred_col.append(y_pred.item())
            pred.append(torch.argmax(y_pred))
            label.append(train_label.item())

            # print('y_pred: {}\t label: {}'.format(y_pred, train_label))
            # print(y_pred.size())
            y_pred = y_pred.view((1, -1))
            train_label = torch.LongTensor([train_label])
            # Compute loss
            loss = criterion(y_pred, train_label)
            acc.append(
                torch.eq(
                    torch.argmax(y_pred),
                    train_label)
            )
            losses.append(loss.item())

            # perform a backward pass, and update the weights.
            loss.backward()
            optimizer.step()

        train_acc = torch.mean(torch.cat(acc).float())
        train_loss = np.mean(losses)

        pred = np.asarray(pred)
        label = np.asarray(label)

        train_pred_out = pred
        train_label_out = label

        train_p2 = pred
        # train_p2[train_p2 >= 0.5] = 1
        # train_p2[train_p2 < 0.5] = 0

        # save new params
        new_state_dict = {}
        for key in model.state_dict():
            new_state_dict[key] = model.state_dict()[key].clone()

        # compare params
        for key in old_state_dict:
            if (old_state_dict[key] == new_state_dict[key]).all():
                print('Not updated in {}'.format(key))

        # dev loss
        losses, acc = [], []
        label, pred = [], []
        model.eval()
        for dev_data, dev_label in dev_dataloader:
            q += 1
            if q % 100 == 0:
                print(q)
            # Squeeze the data [1, 33, 49], [1,5] to [33, 49], [5]
            dev_data = torch.squeeze(dev_data)
            dev_label = torch.squeeze(dev_label)

            # Forward pass : Compute predicted y by passing train data to the model
            y_pred = model(dev_data)

            # Save predict and label
            pred.append(torch.argmax(y_pred))
            label.append(dev_label.item())

            # Compute loss
            y_pred = y_pred.view((1, -1))
            dev_label = torch.LongTensor([dev_label])
            loss = criterion(y_pred, dev_label)
            acc.append(
                torch.eq(
                    torch.argmax(y_pred),
                    dev_label)
            )
            losses.append(loss.item())

        dev_acc = torch.mean(torch.cat(acc).float())
        dev_loss = np.mean(losses)

        pred = np.asarray(pred)
        label = np.asarray(label)

        dev_pred_out = pred
        dev_label_out = label

        dev_p2 = pred
        # dev_p2[dev_p2 >= 0.5] = 1
        # dev_p2[dev_p2 < 0.5] = 0

        # test loss
        losses, acc = [], []
        label, pred = [], []
        model.eval()
        for test_data, test_label in test_dataloader:
            q += 1
            if q % 100 == 0:
                print(q)
            # Squeeze the data [1, 33, 49], [1,5] to [33, 49], [5]
            test_data = torch.squeeze(test_data)
            test_label = torch.squeeze(test_label)

            # Forward pass : Compute predicted y by passing train data to the model
            y_pred = model(test_data)

            # Save predict and label
            pred.append(np.argmax(y_pred.detach().numpy()))
            label.append(test_label.item())

            # Compute loss
            y_pred = y_pred.view((1, -1))
            test_label = torch.LongTensor([test_label])

            loss = criterion(y_pred, test_label)
            acc.append(
                torch.eq(
                    torch.argmax(y_pred),
                    test_label)
            )
            losses.append(loss.item())

        test_acc = torch.mean(torch.cat(acc).float())
        test_loss = np.mean(losses)

        test_pred_out = pred
        test_label_out = label

        epoch_losses.append([
            train_loss, dev_loss, test_loss,
            train_acc, dev_acc, test_acc,
            train_pred_out, dev_pred_out, test_pred_out,
            train_label_out, dev_label_out, test_label_out,
        ])

        pred = np.asarray(pred)
        label = np.asarray(label)
        # print(train_acc, dev_acc, test_acc)
        # print(pred, label)
        # auc_score = roc_auc_score(label, pred)
        test_p2 = pred
        # test_p2[test_p2 >= 0.5] = 1
        # test_p2[test_p2 < 0.5] = 0
        # print(p2, label)
        # print(precision_recall_fscore_support(label,p2,average='weighted'))

        # print("Epoch: {} Train: {:.4f}/{:.2f}%, Dev: {:.4f}/{:.2f}%, Test: {:.4f}/{:.2f}% AUC: {:.4f}".format(
        #     epoch, train_loss, train_acc*100, dev_loss, dev_acc*100, test_loss, test_acc*100, auc_score))
        print("Epoch: {} Train loss: {:.4f}, Dev loss: {:.4f}, Test loss: {:.4f}".format(
            epoch, train_loss, dev_loss, test_loss))
        prf_train = precision_recall_fscore_support(train_label_out, train_p2, average='weighted')
        prf_val = precision_recall_fscore_support(dev_label_out, dev_p2, average='weighted')
        prf_test = precision_recall_fscore_support(test_label_out, test_p2, average='weighted')

        print("TRAIN PRF: " + str(prf_train))
        print("VAL PRF: " + str(prf_val))
        print("TEST PRF: " + str(prf_test))

        fscores_train.append(prf_train[2])
        fscores_val.append(prf_val[2])
        fscores_test.append(prf_test[2])
        graph_epochs.append(epoch)

        fig = plt.figure()
        ax = plt.subplot(1, 1, 1)
        # Train
        plt.plot(graph_epochs, fscores_train, color='red', label='Train')
        # Val
        plt.plot(graph_epochs, fscores_val, color='blue', label='Val')
        # Test
        plt.plot(graph_epochs, fscores_test, color='green', label='Test')

        plt.xlabel("Epochs")
        plt.ylabel('F-score')
        plt.title('GRU-D Osaka')
        plt.xticks([])
        ax.legend()
        plt.savefig(str(epoch) + "_GRUD_osaka_500_final_correctsplit.jpg")
        # plt.show()
        # save the parameters
        train_log = []
        train_log.append(model.state_dict())
        torch.save(model.state_dict(), './save/grud_mean_grud_para.pt')

        # print(train_log)

    return epoch_losses


# In[9]:


def plot_roc_and_auc_score(outputs, labels, title):
    false_positive_rate, true_positive_rate, threshold = roc_curve(labels, outputs)
    auc_score = roc_auc_score(labels, outputs)
    plt.plot(false_positive_rate, true_positive_rate, label='ROC curve, AREA = {:.4f}'.format(auc_score))
    plt.plot([0, 1], [0, 1], 'red')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.axis([0, 1, 0, 1])
    plt.title(title)
    plt.legend(loc='lower right')
    plt.show()


# In[10]:


input_size = 21  # num of variables base on the paper
hidden_size = 21  # same as inputsize
output_size = 3
num_layers = 500  # num of step or layers base on the paper

x_mean = torch.Tensor(np.load('./input/x_mean_osaka_1185.npy'))
x_median = torch.Tensor(np.load('./input/x_median_osaka_1185.npy'))

# In[23]:


# dropout_type : Moon, Gal, mloss
model = GRUD(input_size=input_size, hidden_size=hidden_size, output_size=output_size, dropout=0.1, dropout_type='mloss',
             x_mean=x_mean, num_layers=num_layers)

# load the parameters
# model.load_state_dict(torch.load('./save/grud_para.pt'))
# model.eval()

count = count_parameters(model)
print('number of parameters : ', count)
print(list(model.parameters())[0].grad)

criterion = torch.nn.CrossEntropyLoss()

# In[24]:


'''
def fit(model, criterion, learning_rate,\
        train_dataloader, dev_dataloader, test_dataloader,\
        learning_rate_decay=0, n_epochs=30):
'''
learning_rate = 0.05
learning_rate_decay = 10
n_epochs = 30

# learning_rate = 0.1 learning_rate_decay=True
epoch_losses = fit(model, criterion, learning_rate, train_dataloader, dev_dataloader, test_dataloader,
                   learning_rate_decay, n_epochs)

# In[25]:


# test_preds, test_labels = epoch_losses[11][8], epoch_losses[11][11]

# plot_roc_and_auc_score(test_preds, test_labels, 'GRU-D PhysioNet mortality prediction')

# In[ ]:

