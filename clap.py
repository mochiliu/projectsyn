class ClapAnalyzer:
    def __init__(self, note_lengths, deviation_threshold=0.1):
        """
        :param note_lengths: Relative note lengths in the rhythmic pattern. F.ex. [2, 1, 1, 2, 2]
        :param deviation_threshold: How much deviation from the pattern should be considered failure
        :return:
        """
        self.buffer_size = len(note_lengths)
        self.pattern = self.note_lengths_to_normalized_pauses(note_lengths)
        self.pattern_sum = sum(self.pattern)
        self.min_pattern_time = .01 * self.pattern_sum  # min 100 ms between fastest clap in sequence
        self.max_pattern_time = .7 * self.pattern_sum  # max 500 ms between fastest clap in sequence
        self.clap_times = [None] * self.buffer_size
        self.deviation_threshold = deviation_threshold
        self.current_index = 0
        self.clap_listeners = set()
        self.clap_sequence_listeners = set()

    @staticmethod
    def note_lengths_to_normalized_pauses(note_lengths):
        note_lengths.pop()  # Because the length of the last note doesn't matter
        min_note_length = float(min(note_lengths))
        return list(map(lambda x: x / min_note_length, note_lengths))

    def on_clap(self, fn):
        self.clap_listeners.add(fn)

    def on_clap_sequence(self, fn):
        self.clap_sequence_listeners.add(fn)

    def clap(self, time):
        """
        Tell ClapAnalyzer that a clap has been detected at the specified time
        :param time: Absolute time in seconds. Must be float.
        :return:
        """
        for fn in self.clap_listeners:
            fn()

        self.current_index = (self.current_index + 1) % self.buffer_size
        self.clap_times[self.current_index] = time

        first_clap_in_sequence = self.clap_times[self.current_index - self.buffer_size + 1]
        if first_clap_in_sequence is None:
            return  # waiting for more claps

        time_diff = time - first_clap_in_sequence
        avg_time_per_clap_unit = time_diff / self.pattern_sum
        if self.min_pattern_time <= time_diff <= self.max_pattern_time:
            total_deviation = 0
            j = 0
            for i in range(self.current_index - self.buffer_size + 1, self.current_index):
                clap_time_diff = self.clap_times[i + 1] - self.clap_times[i]
                relative_clap_time_diff = clap_time_diff / avg_time_per_clap_unit
                total_deviation += (relative_clap_time_diff - self.pattern[j]) ** 2
                j += 1

            if total_deviation < self.deviation_threshold:
                for fn in self.clap_sequence_listeners:
                    fn()
                return  # clap sequence detected!
            else:
                return  # clap sequence didn't match accurately enough with the pattern
        else:
            return  # clap sequence too short or too long
     
def clap_sequence_callback():
    print('clap sequence detected')

if __name__ == "__main__":
#    clap_analyzer = ClapAnalyzer(
#            note_lengths=[1./4, 1./8, 1./8, 1./4, 1./4],
#            deviation_threshold=0.1)
    clap_analyzer = ClapAnalyzer(
        note_lengths=[1./4, 1./8, 1./8, 1./4, 1./4],
        deviation_threshold=0.2)
    clap_analyzer.on_clap_sequence(clap_sequence_callback)
    clap_analyzer.clap(0.5988639999999998)
    clap_analyzer.clap(0.6816079999999998)
    clap_analyzer.clap(0.7371049999999997)
    clap_analyzer.clap(0.7925519999999997)
    clap_analyzer.clap(0.8724659999999993)
    print('testdone')
