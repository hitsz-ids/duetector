# Benchmark [#12](https://github.com/hitsz-ids/duetector/issues/12)

Benchmark is a test to evaluate the performance of a system. In this project, we use benchmark to evaluate the performance of `duetector`. The benchmark is divided into three parts: baseline test, production-simulation test and high-load test.

## 1. Baseline Testing

Baseline testing gives a baseline performance of the system. It is used to evaluate the performance of the system under simple conditions.

### 1.1 Performance indicators

We using the following indicators to evaluate the performance of the system:

1. CPU usage
1. Memory usage
1. Disk usage
1. Latency

The reason for choosing these indicators is that they are the most important indicators and most eBPF-releated performance indicators.

### 1.2 Steps

1. Start `duetector` with specified configuration.
1. Writing files to the monitored directory at a specified rate.
1. During the test, record the performance indicators of the system.

### 1.3 Benefits

By baseline testing, we can get the baseline performance of the system. It can be used to compare the performance of the system under different configurations and different versions.

## 2. Production-simulation Testing

Production-simulation testing is used to simulate the production environment. It is used to evaluate the performance of the system under complex conditions.

For the time being, we set the task load for simulating the production environment as **a deep learning task on some single machine**.

### 2.1 Performance indicators

The performance indicators are the same as baseline testing.

### 2.2 Steps

1. Start `duetector` with specified configuration.
1. Start a deep learning task on the same machine, with following characteristics:
   1. With data pre-processing and post-processing.
   1. Traing model with GPU if possible.
   1. Writing model files and check points to the monitored directory at a specified rate.
   1. Verify the model with test data.
1. During the test, record the performance indicators of the system.

### 2.3 Benefits

By production-simulation testing, we can get the performance of the system under complex conditions. It can be used to evaluate the performance of the system under the production environment. User may replace the deep learning task with other tasks, and use this test to evaluate the performance of the system under the production environment.

## 3. High-load Testing

High-load testing is used to evaluate the performance of the system under high-load conditions.

For that time being, we set the task load for high-load testing as **Some high-load tasks on some single machine**.

### 3.1 Performance indicators

Despite the performance indicators in baseline testing, we also use the following indicators to evaluate the performance of the system:

- Start-up time: `bcc` needs to compile the eBPF program before running it.
- Stability: Does the system crash during the test? Or does the system have other problems?(drop packets, etc.)

### 3.2 Steps

1. Start some high-load tasks on the same machine, with following characteristics:
   1. High CPU usage.
   1. High memory usage.
   1. High disk usage.
   1. They can be some deep learning tasks, or some other tasks.
1. Start `duetector` with specified configuration.
1. Perform baseline testing and production-simulation testing at the same time.
1. During the test, record the performance indicators of the system.

### 3.3 Benefits

By high-load testing, we can get the stability of the system under high-load conditions. Which is very important for the production environment.

## Available Tools

Our performance record tool should not affect the performance of the system.
