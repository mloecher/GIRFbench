def get_trigger_times(seq_in):
    blocks = seq_in.block_events

    all_t_trigger = []
    curr_dur = 0
    for block_counter in blocks:
        block = seq_in.get_block(block_counter)
        if hasattr(block, 'trigger'):
            t_trigger = curr_dur + block.trigger[0].duration
            # print(block.trigger, t_trigger)
            all_t_trigger.append(t_trigger)
        curr_dur += seq_in.block_durations[block_counter]
        
    return all_t_trigger