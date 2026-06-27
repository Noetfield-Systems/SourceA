export declare function pingRedis(url?: string): Promise<boolean>;
/** Ensure Redis is reachable — waits for peer boot, then starts embedded dev Redis once. */
export declare function ensureRedis(): Promise<string>;
export declare function stopEmbeddedRedis(): Promise<void>;
