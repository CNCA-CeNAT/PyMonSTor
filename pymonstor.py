#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Imports and definitions
import datetime as dt
import untangle as utan
import matplotlib.pyplot as plt
import re
import sys
import os
import glob
import xml.sax
from collections import OrderedDict as ordict

###############################################################################
# adds a global root to the log file to make it xml standard compliant ########
###############################################################################


def line_prepender(filename, first_line, end_line):
    # with open(filename, 'r+', encoding='utf-8') as f:
    if(os.path.exists(filename) and os.stat(filename).st_size > 0):
        with open(filename, 'r') as f1:
            text = f1.read()
            ntext = re.sub(r'<sched_hint>.+?</sched_hint>', '', text,
                           flags=re.M | re.DOTALL)

        with open(filename, 'w') as fout:
            fout.write(ntext)

        with open(filename, 'r+') as f:
            filt = f.readlines()
            try:
                if filt[0] != '<parent>\n':
                    # f.write(end_line + '\n')
                    # with open(filename, 'r+', encoding='utf-8') as f:
                    with open(filename, 'r+') as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write(first_line.rstrip('\r\n') + '\n' + content)
                    # with open(filename, 'a', encoding='utf-8') as f:
                    with open(filename, 'a') as f:
                        f.write(end_line + '\n')
            except IndexError:
                try:
                    if filt[1] != '<parent>\n':
                        # f.write(end_line + '\n')
                        # with open(filename, 'r+', encoding='utf-8') as f:
                        with open(filename, 'r+') as f:
                            content = f.read()
                            f.seek(0, 0)
                            f.write(first_line.rstrip('\r\n') + '\n' + content)
                            # with open(filename, 'a', encoding='utf-8') as f:
                        with open(filename, 'a') as f:
                            f.write(end_line + '\n')
                except IndexError:
                    pass

###############################################################################
# Generates the log file name to be parsed#####################################
###############################################################################


def gen_logname():
    return dt.date.today().strftime('%Y%m%d')

###############################################################################
# Collects global usage data from torque log files.############################
###############################################################################


def get_global_data(log):
    walltime = 0
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    walltime = walltime + \
                        int(
                            log.parent.Jobinfo[i].resources_used.walltime.cdata
                            )
                    break
                except IndexError:
                    break
                except AttributeError:
                    break
    except TypeError:
        walltime = walltime + \
            int(log.parent.Jobinfo.resources_used.walltime.cdata)
    except IndexError:
        return walltime

    return walltime

###############################################################################
# Collects specified queue usage data from torque log files.###################
###############################################################################


def get_queue_data(log, queue):
    walltime = 0
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    if log.parent.Jobinfo[i].queue.cdata == queue:
                        walltime = walltime + \
                            int(
                                log.parent.Jobinfo[i].resources_used.walltime
                                .cdata
                                )
                        break
                    else:
                        break
                except IndexError:
                    break
                except AttributeError:
                    break
    except TypeError:
        if log.parent.Jobinfo.queue.cdata == queue:
            walltime = walltime + \
                int(
                    log.parent.Jobinfo.resources_used.walltime.cdata
                    )
    except IndexError:
        return walltime

    return walltime

###############################################################################
# Collects specified node usage data from torque log files.####################
###############################################################################


def get_node_data(log, node):
    walltime = 0
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    if log.parent.Jobinfo[i].exec_host.cdata.count(node) >= 1:
                        walltime = walltime +\
                            int(
                                log.parent.Jobinfo[i].resources_used.walltime
                                .cdata
                                )
                        break
                    else:
                        break
                except IndexError:
                    break
                except AttributeError:
                    break
    except TypeError:
        if log.parent.Jobinfo.exec_host.cdata.count(node) >= 1:
            walltime = walltime + \
                int(
                    log.parent.Jobinfo.resources_used.walltime.cdata
                    )
    except IndexError:
        return walltime

    return walltime

###############################################################################
# Collects users data from torque log files.###################################
###############################################################################


def get_user_data(log, user):
    walltime = 0
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    if log.parent.Jobinfo[i].Job_Owner.cdata.count(user) >= 1:
                        walltime = walltime +\
                            int(
                                log.parent.Jobinfo[i].resources_used.walltime
                                .cdata
                                )
                        break
                    else:
                        break
                except IndexError:
                    break
                except AttributeError:
                    break
    except TypeError:
        if log.parent.Jobinfo.Job_Owner.cdata.count(user) >= 1:
            walltime = walltime +\
                int(
                    log.parent.Jobinfo.resources_used.walltime.cdata
                    )
    except IndexError:
        return walltime

    return walltime

###############################################################################
# Gets users from log file and creates a dictionary############################
###############################################################################


def user_dict(log):
    user = {}
    # If the log file has a single entry, this will catch the TypeError
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    # Extracts the user name from the log file and assings it
                    # as a dictionary key with default value 0
                    user[re.search('(.+?)@',
                         log.parent.Jobinfo[i].Job_Owner.cdata).group(1)] = 0
                    break
                except IndexError:
                    break
                except AttributeError:
                    break
        return user
    except TypeError:
        user[re.search('(.+?)@', log.parent.Jobinfo.Job_Owner.cdata)
             .group(1)] = 0
    except IndexError:
        return user

    return user

###############################################################################
# Gets start and end of job times and returns array ###########################
###############################################################################


def time_interval(log):
    start_time = []
    # If the log file has a single entry, this will catch the TypeError
    try:
        for i in range(len(log.parent.Jobinfo)):
            while True:
                try:
                    # Extracts the start time from the log file and appends it
                    # to the list
                    start_time.append(dt.datetime.fromtimestamp(int(log.parent.
                                      Jobinfo[i].start_time.cdata)))
                    break
                except IndexError:
                    break
                except AttributeError:
                    break
        return start_time
    except TypeError:
        start_time.append(0)
    except IndexError:
        return start_time

    return start_time

###############################################################################
# FOR block range_report log dictionary #######################################
###############################################################################


def log_for_fill(dataA, dataB, logs):
    for i in range(dataA, dataB):
        try:
            logs.extend([str(i)])
        except IndexError:
            print("Log file " + i + " does not exist.")
    return logs

###############################################################################
# Fill range_report log dictionary ############################################
###############################################################################


def range_log_fill(day0, day1):
    # Reference when interval includes different months
    trunk_day0 = round(int(day0), -2) + 1
    diff = abs(int(day0) - int(day1))
    logs = []

    if diff <= 30:
        log_for_fill(int(day0), int(day0) + diff + 1, logs)

    else:
        if 100 <= diff <= 1200:
            rounder = (round(diff, -2))/100
            for j in range(0, rounder + 1):
                if j == 0:
                    log_for_fill(int(day0), int(day0) + diff + 1, logs)
                elif j == rounder + 1:
                    log_for_fill(trunk_day0 + j, int(day1), logs)
                else:
                    log_for_fill(trunk_day0 + j, 32, logs)

    return logs

###############################################################################
# Collects data from specified month in yyyymm format##########################
###############################################################################


def month_report(month):

    # Normal variables for Service unit calculations
    # su_cadejos = 432000  # Seconds or 120 hours/Service Units per day
    # su_zarate = 345600  # Seconds or 96 hours/Service Units per day
    # su_total = su_cadejos + su_zarate

    # Creates dictionaries
    nodes = dictionary_init("nodes")
    queues = dictionary_init("queues")
    users = dictionary_init(" ")
    days = dictionary_init("days")
    hours = dictionary_init("hours")
    hours = order_key(hours)

# Creates a list of log file names
    logs = glob.glob(month+"*")

# Collects data from log files in the list
    for i in logs:
        # print(i)
        line_prepender(i, '<parent>', '</parent>')
        try:
            parsed = utan.parse(i)
            users.update(user_dict(parsed))
        except xml.sax.SAXParseException:
            pass

    # Gets data using defined functions and normalices data to
    # Service Units (SU)
    for i in logs:
        try:
            parsed = utan.parse(i)
            update_dicts(queues, users, nodes, days, hours, parsed)
        except xml.sax.SAXParseException:
            pass

# Sums collected data for plot
    sum_data(queues)

# Orders elements in dictionaries
    # sorted_nodes = order_dict(nodes)
    sorted_queues = order_dict(queues)
    sorted_users = order_dict(users)

# Plots data
    gen_plots(sorted_users, sorted_queues, days, hours, month)
    pie_plots(sorted_users, sorted_queues, month, '-m')

###############################################################################
# Generate a report of the specified year #####################################
###############################################################################


def year_report(year):

    # Creates dictionaries
    nodes = dictionary_init("nodes")
    queues = dictionary_init("queues")
    users = dictionary_init(" ")
    days = dictionary_init("days")
    hours = dictionary_init("hours")
    hours = order_key(hours)

# Creates a list of log file names
    logs = glob.glob(year+"*")
    # print(logs)

# Collects data from log files in the list
    for i in logs:
        line_prepender(i, '<parent>', '</parent>')
        try:
            parsed = utan.parse(i)
            users.update(user_dict(parsed))
        except xml.sax.SAXParseException:
            pass

    # Gets data using defined functions and normalices data
    # to Service Units (SU)
    for i in logs:
        try:
            parsed = utan.parse(i)
            update_dicts(queues, users, nodes, days, hours, parsed)
        except xml.sax.SAXParseException:
            pass

# Sums collected data for plot
    sum_data(queues)

# Orders elements in dictionaries
    sorted_queues = order_dict(queues)
    sorted_users = order_dict(users)

# Plots data
    gen_plots(sorted_users, sorted_queues, days, hours, year)
    pie_plots(sorted_users, sorted_queues, year, '-y')

###############################################################################
# Generate today's report #####################################################
###############################################################################


def today_report(today):

    # Creates dictionaries
    nodes = dictionary_init("nodes")
    queues = dictionary_init("queues")
    users = dictionary_init(" ")
    days = dictionary_init("days")
    hours = dictionary_init("hours")
    hours = order_key(hours)

    line_prepender(gen_logname(), '<parent>', '</parent>')
    try:
        parsed = utan.parse(gen_logname())
        users.update(user_dict(parsed))
    except xml.sax.SAXParseException:
        pass

# Gets data using defined functions and normalices data
# to Service Units (SU)
    try:
        update_dicts(queues, users, nodes, days, hours, parsed)
    except xml.sax.SAXParseException:
        pass

# Sums collected data for plot
    sum_data(queues)

# Orders elements in dictionaries
    sorted_queues = order_dict(queues)
    sorted_users = order_dict(users)

# Plots data
    gen_plots(sorted_users, sorted_queues, days, hours, gen_logname())
    pie_plots(sorted_users, sorted_queues, gen_logname(), '-t')

###############################################################################
# Specific day report #########################################################
###############################################################################


def day_report(day):

    # Creates dictionaries
    nodes = dictionary_init("nodes")
    queues = dictionary_init("queues")
    users = dictionary_init(" ")
    days = dictionary_init("days")
    hours = dictionary_init("hours")
    hours = order_key(hours)

    line_prepender(day, '<parent>', '</parent>')
    try:
        parsed = utan.parse(day)
        users.update(user_dict(parsed))
    except xml.sax.SAXParseException:
        pass

# Gets data using defined functions and normalices data to Service Units (SU)
    try:
        update_dicts(queues, users, nodes, days, hours, parsed)
    except xml.sax.SAXParseException:
        pass

# Sums collected data for plot
    sum_data(queues)

# Orders elements in dictionaries
    sorted_queues = order_dict(queues)
    sorted_users = order_dict(users)

# Plots data
    gen_plots(sorted_users, sorted_queues, days, hours, day)
    pie_plots(sorted_users, sorted_queues, day, '-d')

###############################################################################
# Report using log files from a range of dates ################################
###############################################################################


def range_report(day0, day1):

    # Variable for when the interval is in the same month or not
    logs = []

    # Checks if arguments were given in the correct order. If not, inverts them
    if int(day0) < int(day1):
        logs.extend(range_log_fill(int(day0), int(day1)))

    else:
        logs.extend(range_log_fill(int(day1), int(day0)))

    # Creates dictionaries
    nodes = dictionary_init("nodes")
    queues = dictionary_init("queues")
    users = dictionary_init(" ")
    days = dictionary_init("days")
    hours = dictionary_init("hours")
    hours = order_key(hours)

# Collects data from log files in the list
    for i in logs:
        line_prepender(i, '<parent>', '</parent>')
        try:
            parsed = utan.parse(i)
            users.update(user_dict(parsed))
        except xml.sax.SAXParseException:
            pass

    # Gets data using defined functions and normalices data
    # to Service Units (SU)
    for i in logs:
        try:
            parsed = utan.parse(i)
            update_dicts(queues, users, nodes, days, hours, parsed)
        except xml.sax.SAXParseException:
            pass

# Sums collected data for plot
    sum_data(queues)

# Orders elements in dictionaries
    sorted_queues = order_dict(queues)
    sorted_users = order_dict(users)

# Plots data
    gen_plots(sorted_users, sorted_queues, days, hours,
              "Range " + day0 + " - " + day1)
    pie_plots(sorted_users, sorted_queues, "Range " + day0 + " - " + day1,
              '-r')

###############################################################################
# Creates dictionaries ########################################################
###############################################################################


def dictionary_init(option):
    if option == "nodes":
        return {'cadejos-0': 0, 'cadejos-1': 0, 'cadejos-2': 0, 'cadejos-3': 0,
                'cadejos-4': 0, 'zarate-0a': 0, 'zarate-0b': 0, 'zarate-0c': 0,
                'zarate-0d': 0, 'zarate-1a': 0, 'zarate-1b': 0, 'zarate-1c': 0,
                'zarate-1d': 0, 'zarate-2a': 0, 'zarate-2b': 0, 'zarate-2c': 0,
                'zarate-2d': 0, 'zarate-3a': 0, 'zarate-3b': 0, 'zarate-3c': 0,
                'zarate-3d': 0, 'zarate-4a': 0, 'zarate-4b': 0, 'zarate-4c': 0,
                'zarate-4d': 0, 'tule-00': 0, 'tule-01': 0, 'tule-02': 0,
                'tule-03': 0}
    elif option == "queues":
        return {'total': 0, 'cadejos': 0, 'zarate': 0, 'tule': 0,
                'cpu-n4h24': 0, 'cpu-n3h72': 0, 'cpu-n5h24': 0, 'gpu-n2h24': 0,
                'gpu-n1h72': 0, 'phi-debug': 0, 'phi-n2h72': 0, 'phi-n3h24': 0,
                'phi-n5h24': 0, 'phi-n6h24': 0, 'phi-n1h72': 0, 'phi-n6h96': 0,
                'phi-n18h72': 0, 'debug': 0, 'k40': 0, 'cpu-debug': 0,
                'gpu-debug': 0}
    elif option == "days":
        d = ordict()
        d["Monday"] = 0
        d["Tuesday"] = 0
        d["Wednesday"] = 0
        d["Thursday"] = 0
        d["Friday"] = 0
        d["Saturday"] = 0
        d["Sunday"] = 0
        return d
    elif option == "hours":
        return {'00:00 - 01:00': 0, '01:00 - 02:00': 0, '02:00 - 03:00': 0,
                '03:00 - 04:00': 0, '04:00 - 05:00': 0, '05:00 - 06:00': 0,
                '06:00 - 07:00': 0, '07:00 - 08:00': 0, '08:00 - 09:00': 0,
                '09:00 - 10:00': 0, '10:00 - 11:00': 0, '11:00 - 12:00': 0,
                '12:00 - 13:00': 0, '13:00 - 14:00': 0, '14:00 - 15:00': 0,
                '15:00 - 16:00': 0, '16:00 - 17:00': 0, '17:00 - 18:00': 0,
                '18:00 - 19:00': 0, '19:00 - 20:00': 0, '20:00 - 21:00': 0,
                '21:00 - 22:00': 0, '22:00 - 23:00': 0, '23:00 - 24:00': 0}
    else:
        return {}

###############################################################################
# Sums data in dictionaries ###################################################
###############################################################################


def sum_data(queues):
    # queues['cadejos'] = queues['cpu-debug'] + queues['debug'] + \
    #     queues['cpu-n4h24'] + queues['cpu-n3h72']
    queues['cadejos'] = queues['cpu-debug'] + \
        queues['cpu-n4h24'] + queues['cpu-n3h72']
    queues['tule'] = queues['gpu-debug'] + queues['gpu-n1h72'] + \
        queues['k40'] + queues['gpu-n2h24']
    queues['zarate'] = queues['phi-debug'] + queues['phi-n2h72'] +  \
        queues['phi-n3h24'] + queues['phi-n5h24'] + queues['phi-n6h24'] + \
        queues['phi-n1h72'] + queues['phi-n6h96'] + queues['phi-n18h72'] + \
        queues['debug']
    # queues['total'] = (get_global_data(log))/3600
    queues['total'] = queues['cadejos'] + queues['zarate'] + queues['tule']

###############################################################################
# Orders dictionaries by item #################################################
###############################################################################


def order_dict(queue):
    return ordict(sorted(queue.items(), key=lambda t: t[1], reverse=True))

###############################################################################
# Orders dictionaries by key ##################################################
###############################################################################


def order_key(queue):
    return ordict(sorted(queue.items(), key=lambda t: t[0], reverse=False))

###############################################################################
# Creates plots ###############################################################
###############################################################################


def gen_plots(users, queues, days, hours, name):

    # Plots data in dictionaries
    # Users
    plt.figure(1, figsize=(25, 15))
    fig1, ax1 = plt.subplots()
    rects1 = ax1.bar(range(len(users)), users.values(), align='center')
    plt.title('Service Units per User')
    plt.ylabel('Service Units / SU')
    plt.xlabel('Users')
    plt.bar(range(len(users)), users.values(), align='center')
    plt.xticks(range(len(users)), list(users.keys()), rotation=90)
    autolabel(rects1, ax1, '%.1f')
    plt.tight_layout()
    plt.savefig('plot_'+name+'_user_rank.pdf')

    # Global and queues
    plt.figure(2)
    fig2, ax2 = plt.subplots()
    rects2 = ax1.bar(range(len([0, 1, 2, 3])), [queues['total'],
                     queues['zarate'], queues['tule'], queues['cadejos']],
                     align='center')
    plt.title('Service Units per queue')
    plt.ylabel('Service Units / SU')
    plt.xlabel('Queues')
    plt.bar(range(len([0, 1, 2, 3])), [queues['total'], queues['zarate'],
            queues['tule'], queues['cadejos']], align='center')
    plt.xticks(range(len([0, 1, 2, 3])), ['total', 'zarate', 'tule',
               'cadejos'], rotation=0)
    autolabel(rects2, ax2, '%.3f')
    plt.tight_layout()
    plt.savefig('plot_'+name+'_queue_usage.pdf')

    plt.figure(8, figsize=(25, 15))
    fig3, ax3 = plt.subplots()
    rects3 = ax3.bar(range(len(days)), days.values(), align='center')
    plt.title('Usage distribution per day')
    plt.ylabel('Submitted Jobs')
    plt.xlabel('Days')
    plt.bar(range(len(days)), days.values(), align='center')
    plt.xticks(range(len(days)), list(days.keys()), rotation=90)
    autolabel(rects3, ax3, '%d')
    plt.tight_layout()
    plt.savefig('plot_'+name+'_daily_usage.pdf')

    plt.figure(9, figsize=(25, 15))
    fig4, ax4 = plt.subplots()
    rects4 = ax4.bar(range(len(hours)), hours.values(), align='center')
    plt.title('Usage distribution per hour')
    plt.ylabel('Submitted Jobs')
    plt.xlabel('Hour intervals')
    plt.bar(range(len(hours)), hours.values(), align='center')
    plt.xticks(range(len(hours)), list(hours.keys()), rotation=90)
    autolabel(rects4, ax4, '%d')
    plt.tight_layout()
    plt.savefig('plot_'+name+'_hourly_usage.pdf')


def pie_plots(users, queues, name, period):
    su_zarate = 0
    su_cadejos = 0
    su_tule = 0
    delta = 0

    if(period == '-y'):
        su_zarate = 20*24*365
        su_cadejos = 5*24*365
        su_tule = 4*24*365
    elif(period == '-m'):
        if(sys.argv[2][4:] == '01' or sys.argv[2][4:] == '03' or
           sys.argv[2][4:] == '05' or sys.argv[2][4:] == '07' or
           sys.argv[2][4:] == '08' or sys.argv[2][4:] == '10' or
           sys.argv[2][4:] == '12'):
            su_zarate = 18*24*31
            su_cadejos = 5*24*31
            su_tule = 4*24*31
        elif(sys.argv[2][4:] == '04' or sys.argv[2][4:] == '06' or
             sys.argv[2][4:] == '09' or sys.argv[2][4:] == '11'):
            su_zarate = 18*24*30
            su_cadejos = 5*24*30
            su_tule = 4*24*30
        else:
            su_zarate = 18*24*28
            su_cadejos = 5*24*28
            su_tule = 4*24*28
    elif(period == '-d'):
        su_zarate = 18*24
        su_cadejos = 5*24
        su_tule = 4*24
    elif(period == '-t'):
        su_zarate = 18*24
        su_cadejos = 5*24
        su_tule = 4*24
    elif(period == '-r'):
        delta = delta_days(sys.argv[2], sys.argv[3])
        su_zarate = 18*24*delta
        su_cadejos = 5*24*delta
        su_tule = 4*24*delta

    if (queues['zarate'] == 0.0):
        data_zarate = 0.0
    elif(queues['zarate'] < su_zarate):
        data_zarate = su_zarate - queues['zarate']
    else:
        data_zarate = su_zarate - queues['zarate']

    if (queues['cadejos'] == 0.0):
        data_cadejos = 0.0
    else:
        data_cadejos = su_cadejos - queues['cadejos']

    if (queues['tule'] == 0.0):
        data_tule = 0.0
    else:
        data_tule = su_tule - queues['tule']
    # Pie charts for users
    # plt.figure(3)
    # plt.title('Service Units per User')
    # t.pie(list[users.values()], labels=list(users.keys()), autopct='%1.1f%%',
    #         shadow=True, startangle=90)
    # plt.axis('equal')
    # plt.tight_layout()
    # plt.savefig('pie_'+name+'_user_rank.pdf')

    # Pie charts Global
    plt.figure(4, figsize=(7, 7))
    plt.title('Service Units per queue')
    plt.pie([data_zarate, data_tule, data_cadejos], autopct='%1.1f%%',
            shadow=True, startangle=90)
    patches, texts = plt.pie([data_zarate, data_tule, data_cadejos],
                             startangle=90)
    plt.legend(patches, ['zarate', 'tule', 'cadejos'], loc='best')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_'+name+'_queue_usage.pdf')

    plt.figure(5, figsize=(7, 7))
    plt.title('Usage percentage Zarate')
    plt.pie([data_zarate, queues['zarate']], autopct='%1.1f%%', shadow=True,
            startangle=90)
    patches, texts = plt.pie([data_zarate, queues['zarate']], startangle=90)
    plt.legend(patches, ['idle time', 'efective time'], loc='best')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_'+name+'_zarate_usage.pdf')

    plt.figure(6, figsize=(7, 7))
    plt.title('Usage percentage Cadejos')
    plt.pie([data_cadejos, queues['cadejos']], autopct='%1.1f%%', shadow=True,
            startangle=90)
    patches, texts = plt.pie([data_cadejos, queues['cadejos']], startangle=90)
    plt.legend(patches, ['idle time', 'efective time'], loc='best')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_'+name+'_cadejos_usage.pdf')

    plt.figure(7, figsize=(7, 7))
    plt.title('Usage percentage Tule')
    plt.pie([data_tule, queues['tule']], autopct='%1.1f%%', shadow=True,
            startangle=90)
    patches, texts = plt.pie([data_tule, queues['tule']], startangle=90)
    plt.legend(patches, ['idle time', 'efective time'], loc='best')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('pie_'+name+'_tule_usage.pdf')

###############################################################################
# Labels bars #################################################################
# Credits to Lindsey Kuper for the code #######################################
###############################################################################


def autolabel(rects, ax, string_format):

    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()
        # Fraction of axis height taken up by this rectangle
        p_height = (height / y_height)

        # If we can fit the label above the column, do that;
        # otherwise, put it inside the column.
        if p_height > 0.95:  # arbitrary; 95% looked good to me.
            label_position = height - (y_height * 0.05)
        else:
            label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width()/2., label_position,
                string_format % float(height),
                ha='center', va='bottom')

###############################################################################
# Updates dictionaries ########################################################
###############################################################################


def update_dicts(queues, users, nodes, days, hours, parsed_log):
    for j in queues.keys():
        queues[j] = queues[j] + (get_queue_data(parsed_log, j))/3600

    for k in users.keys():
        users[k] = users[k] + (get_user_data(parsed_log, k))/3600

    for l in nodes.keys():
        nodes[l] = nodes[l] + (get_node_data(parsed_log, l))/3600

    day_index = 0
    for m in days.keys():
        day_list = time_interval(parsed_log)
        for i in range(len(day_list)):
            try:
                if (day_list[i].weekday() == day_index):
                    days[m] = days[m] + 1
            except AttributeError:
                pass
        day_index = day_index + 1

    hour_index = 0
    for n in hours.keys():
        hour_list = time_interval(parsed_log)
        for i in range(len(hour_list)):
            try:
                if (day_list[i].hour == hour_index):
                    hours[n] = hours[n] + 1
            except AttributeError:
                pass
        hour_index = hour_index + 1

###############################################################################
# Returns delta date in days ##################################################
###############################################################################


def delta_days(day0, day1):
    dday0 = dt.strptime(day0, '%Y%m%d')
    dday1 = dt.strptime(day1, '%Y%m%d')
    delta = dday1 - dday0
    return abs(int(delta.days))

###############################################################################
###############################################################################
# -m yyyymm
# -y yyyy
# -t today
# -r yyyymmdd yyyymmdd
# -d yyyymmdd
###############################################################################
###############################################################################


def main(argv):

    if(len(sys.argv) >= 2):
        if(sys.argv[1] == '-m'):
            month_report(sys.argv[2])
        elif(sys.argv[1] == '-y'):
            year_report(sys.argv[2])
        elif(sys.argv[1] == '-t'):
            today_report(gen_logname())
        elif(sys.argv[1] == '-r'):
            range_report(sys.argv[2], sys.argv[3])
        elif(sys.argv[1] == '-d'):
            day_report(sys.argv[2])

        else:
            print("error")
    else:
        print("error")

###############################################################################
###############################################################################


if __name__ == "__main__":
    main(sys.argv[1:])

###############################################################################
###############################################################################
