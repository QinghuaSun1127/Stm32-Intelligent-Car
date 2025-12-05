#ifndef __PID_H__
#define __PID_H__

#include "main.h"

// PID structure
typedef struct {
    float Kp; // Proportional Gain
    float Ki; // Integral Gain
    float Kd; // Derivative Gain
    float integral;
    float pre_error;
    float output;
} PID;

// Initialize PID controller
void PID_Init(PID* pid, float Kp, float Ki, float Kd);

// Update PID controller
float PID_Update(PID* pid, float setpoint, float pv, float dt);

#endif /* PID_H */

