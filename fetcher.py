from datetime import date
import requests
import time
import signal
from app import get_db

TOKEN = 'ce43b3dd7ae8402c8f2183a602db8a80'
INTERVAL = 5 * 60


class Fetcher(object):
    base_url = 'https://api-metrika.yandex.ru'

    def __init__(self):
        self.running = True
        self.db = None

    def url(self, path):
        return '{}/{}'.format(self.base_url, path)

    def fetch_counters(self):
        print 'fetch counters'
        try:
            data = requests.get(self.url('counters.json'), {
                'oauth_token': TOKEN
            })
        except Exception as e:
            print e
            return None

        return data.json()

    def fetch_stats(self, counter_ids):
        print 'fetch stats'
        date_str = date.today().strftime('%Y%m%d')

        stats = []

        for i, c_id in enumerate(counter_ids):
            print 'fetching stats for {}'.format(c_id)
            try:
                data = requests.get(self.url('stat/traffic/summary.json'), {
                    'id': c_id,
                    'oauth_token': TOKEN,
                    'date1': date_str,
                    'date2': date_str
                })
            except Exception as e:
                print e
            else:
                stats.append(data.json())
            if i > 0 and i % 10 == 0:
                self.store_stats(stats)
                stats = []
        self.store_stats(stats)

    def store_stats(self, stats):
        print 'store_stats'
        data = ((c['totals']['visits'], c['id']) for c in stats)

        cur = self.db.cursor()
        cur.executemany("UPDATE counters SET visits = ? WHERE id = ?", data)
        self.db.commit()

    def run(self):
        while self.running:
            print 'start'
            self.db = get_db()

            try:
                self.fetch()
            except KeyboardInterrupt:
                self.running = False
                print 'stop'
            except Exception as e:
                print e
            else:
                print 'sleep'
                time.sleep(INTERVAL)

        print 'end'
        self.db.close()

    def stop(self):
        self.running = False

    def fetch(self):
        print 'fetch'
        counters = self.fetch_counters()
        if not counters:
            print 'no counters'
            return

        print 'saving counters'
        insert_data = ((c['id'], c['name']) for c in counters['counters'])
        cur = self.db.cursor()
        cur.executemany("INSERT OR IGNORE INTO counters (id, name) VALUES (?, ?)", insert_data)
        self.db.commit()

        self.fetch_stats((c['id'] for c in counters['counters']))


if __name__ == '__main__':
    from app import app

    with app.app_context():
        fetcher = Fetcher()

        def signal_handler(signal, frame):
            print('You pressed Ctrl+C!')
            fetcher.stop()
        signal.signal(signal.SIGINT, signal_handler)

        fetcher.run()

