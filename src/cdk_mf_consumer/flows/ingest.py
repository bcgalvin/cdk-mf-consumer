from datetime import datetime
from pathlib import Path
from time import sleep

from metaflow import FlowSpec, Parameter, step

from cdk_mf_consumer.client import HNClient
from cdk_mf_consumer.data import HNData, process_batch, process_user_batch
from cdk_mf_consumer.utils import get_partitioned_path


class HNIngestFlow(FlowSpec):
    
    BATCH_SIZE = 50
    RATE_LIMIT_DELAY = 0.5
    OUTPUT_DIR = "data/raw"
    

    @step
    def start(self):
        print("Starting HN data ingestion")
        self.output_dir = Path(self.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.item_stats = {
            "success": 0, "failed": 0, "not_found": 0,
            "success_story": 0, "success_comment": 0,
            "success_job": 0, "success_poll": 0,
            "success_pollopt": 0
        }
        self.user_stats = {"success": 0, "failed": 0, "not_found": 0}
        self.start_time = datetime.now()
        
        self.next(self.get_updates)

    @step
    def get_updates(self):
        """Fetch updates from HackerNews API."""
        client = HNClient()
        self.updates = client.get_updates()
        
        if not self.updates or not self.updates.items:
            print("No updates available")
        else:
            print(f"Processing {len(self.updates.items)} items in batches of {self.BATCH_SIZE}")
        self.next(self.process_items)

    @step
    def process_items(self):
        client = HNClient()
        self.all_items = []
        
        for i in range(0, len(self.updates.items), self.BATCH_SIZE):
            batch_items = self.updates.items[i:i + self.BATCH_SIZE]
            items = process_batch(client, batch_items, self.item_stats)
            self.all_items.extend(items)
            
            current = i + len(batch_items)
            success_rate = (self.item_stats["success"] / current) * 100 if current > 0 else 0
            print(
                f"Items Progress: {current}/{len(self.updates.items)} ({current/len(self.updates.items)*100:.1f}%) | "
                f"Success: {self.item_stats['success']} ({success_rate:.1f}%) | "
                f"By Type: Stories={self.item_stats['success_story']}, "
                f"Comments={self.item_stats['success_comment']}, "
                f"Jobs={self.item_stats['success_job']}, "
                f"Polls={self.item_stats['success_poll']}, "
                f"PollOpts={self.item_stats['success_pollopt']} | "
                f"Failed: {self.item_stats['failed']} | Not Found: {self.item_stats['not_found']}"
            )
            
            if i + self.BATCH_SIZE < len(self.updates.items):
                sleep(self.RATE_LIMIT_DELAY)
        
        self.next(self.process_users)

    @step
    def process_users(self):
        client = HNClient()
        self.all_users = []
        
        print(f"Processing {len(self.updates.profiles)} users in batches of {self.BATCH_SIZE}")
        for i in range(0, len(self.updates.profiles), self.BATCH_SIZE):
            batch_profiles = self.updates.profiles[i:i + self.BATCH_SIZE]
            users = process_user_batch(client, batch_profiles, self.user_stats)
            self.all_users.extend(users)
            
            current = i + len(batch_profiles)
            success_rate = (self.user_stats["success"] / current) * 100 if current > 0 else 0
            print(
                f"Users Progress: {current}/{len(self.updates.profiles)} ({current/len(self.updates.profiles)*100:.1f}%) | "
                f"Success: {self.user_stats['success']} ({success_rate:.1f}%) | "
                f"Failed: {self.user_stats['failed']} | Not Found: {self.user_stats['not_found']}"
            )
            
            if i + self.BATCH_SIZE < len(self.updates.profiles):
                sleep(self.RATE_LIMIT_DELAY)
        
        self.next(self.save_data)

    @step
    def save_data(self):
        if not self.all_items and not self.all_users:
            print("No items or users were successfully processed")
            self.output_paths = {}
            self.next(self.end)
            return
            
        self.output_paths = {}
        hn_data = HNData()
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        if self.all_items:
            item_frames = hn_data.items_to_frames(self.all_items)
            
            for item_type, df in item_frames.items():
                if df is not None:
                    plural_type = HNData.get_plural_form(item_type)
                    partitioned_path = get_partitioned_path(self.output_dir, plural_type, timestamp)
                    partitioned_path.mkdir(parents=True, exist_ok=True)
                    output_path = partitioned_path / f"{timestamp_str}.parquet"
                    print(f"Writing {len(df)} {plural_type} to {output_path}")
                    hn_data.write_parquet(df, output_path, compression="snappy")
                    self.output_paths[item_type] = output_path
        
        if self.all_users:
            plural_type = HNData.get_plural_form("user")
            partitioned_path = get_partitioned_path(self.output_dir, plural_type, timestamp)
            partitioned_path.mkdir(parents=True, exist_ok=True)
            users_df = hn_data.users_to_frame(self.all_users, timestamp)
            users_path = partitioned_path / f"{timestamp_str}.parquet"
            print(f"Writing {len(users_df)} users to {users_path}")
            hn_data.write_parquet(users_df, users_path, compression="snappy")
            self.output_paths["user"] = users_path
            
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    HNIngestFlow()
