namespace Statistics
{
    using System.Collections.Generic;

    public class TreeStatistics
    {
        public int Num { get; set; } = 0;
        public int MinSize { get; set; } = 0;
        public int MaxSize { get; set; } = 0;
        public int SumSize { get; set; } = 0;
        public double AvgSize { get; set; } = 0;
        public int SumWeight { get; set; } = 0;
        public int AvgWeight { get; set; } = 0;
        public int MinWeight { get; set; } = 0;
        public int MaxWeight { get; set; } = 0;
        public int NumEdges { get; set; } = 0;
        public int Width { get; set; } = 0;
        public int Height { get; set; } = 0;
        public int DegreesVar { get; set; } = 0;
        public int Diameter { get; set; } = 0;
        public double MaxCliqueDistribution { get; set; } = 0;
        public Dictionary<int, int> DistributionSize { get; set; } = new Dictionary<int, int>();
        public Dictionary<int, int> DistributionWeight { get; set; } = new Dictionary<int, int>();
    }

    public class Stats
    {
        public Dictionary<string, string> Parameters = new Dictionary<string, string>();
        public Dictionary<string, List<double>> Output = new Dictionary<string, List<double>>();
        public Dictionary<string, List<double>> Times = new Dictionary<string, List<double>>();
        public List<TreeStatistics> CliqueTrees { get; set; } = new List<TreeStatistics>();
    }
}