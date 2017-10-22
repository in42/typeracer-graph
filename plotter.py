import sqlite3
import matplotlib.pyplot as plt

def plot():
    conn = sqlite3.connect('typeracer.db')

    c = conn.cursor()

    c.execute('SELECT speed FROM races')

    data = c.fetchall()
    speeds = [x[0] for x in data[::-1]]

    if len(speeds) < 10:
        print('Atleast need 10 races.')
        quit()

    avg_speeds = []
    curr_sum = sum(speeds[:9])
    for i in range(9, len(speeds)):
        curr_sum = curr_sum + speeds[i]
        avg_speeds.append(curr_sum / 10)
        curr_sum = curr_sum - speeds[i - 9]

    plt.plot(avg_speeds)
    plt.ylabel('Average speed of last 10 races')
    plt.xlabel('No. of races')
    plt.show()

if __name__ == '__main__':
    plot()
