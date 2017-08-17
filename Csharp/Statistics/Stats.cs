namespace Statistics
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class TreeStatistics
    {
        public double Num { get; set; } = 0;
        public double MinSize { get; set; } = 0;
        public double MaxSize { get; set; } = 0;
        public double SumSize { get; set; } = 0;
        public double AvgSize { get; set; } = 0;
        public double SumWeight { get; set; } = 0;
        public double AvgWeight { get; set; } = 0;
        public double MinWeight { get; set; } = 0;
        public double MaxWeight { get; set; } = 0;
        public double NumEdges { get; set; } = 0;
        public double Width { get; set; } = 0;
        public double Height { get; set; } = 0;
        public double DegreesVar { get; set; } = 0;
        public double Diameter { get; set; } = 0;
        public double MaxCliqueDistribution { get; set; } = 0;
        public Dictionary<int, int> DistributionSize { get; set; } = new Dictionary<int, int>();
        public Dictionary<int, int> DistributionWeight { get; set; } = new Dictionary<int, int>();

        public void Add(TreeStatistics other)
        {
            this.Num += other.Num;
            this.NumEdges += other.NumEdges;
            this.AvgSize += other.AvgSize;
            this.AvgWeight += other.AvgWeight;
            this.Width += other.Width;
            this.Height += other.Height;
            this.DegreesVar += other.DegreesVar;
            this.Diameter += other.Diameter;
            this.MaxCliqueDistribution += other.MaxCliqueDistribution;
            this.MaxSize += other.MaxSize;
            this.MinSize += other.MinSize;
            this.MaxWeight += other.MaxWeight;
            this.MinWeight += other.MinWeight;
            this.SumSize += other.SumSize;
            this.SumWeight += other.SumWeight;
        }

        public void Divide(double factor)
        {
            this.Num /= factor;
            this.NumEdges /= factor;
            this.AvgSize /= factor;
            this.AvgWeight /= factor;
            this.Width /= factor;
            this.Height /= factor;
            this.DegreesVar /= factor;
            this.Diameter /= factor;
            this.MaxCliqueDistribution /= factor;
            this.MaxSize /= factor;
            this.MinSize /= factor;
            this.MaxWeight /= factor;
            this.MinWeight /= factor;
            this.SumSize /= factor;
            this.SumWeight /= factor;
        }

        public static List<TreeStatistics> AvgStdTreeStats(List<TreeStatistics> treeStats)
        {
            var avgStats = new TreeStatistics();
            var stdStats = new TreeStatistics();
            var tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.Num));
            avgStats.Num = tmp[0]; stdStats.Num = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.NumEdges));
            avgStats.NumEdges = tmp[0]; stdStats.NumEdges = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.AvgSize));
            avgStats.AvgSize = tmp[0]; stdStats.AvgSize = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.AvgWeight));
            avgStats.AvgWeight = tmp[0]; stdStats.AvgWeight = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.Width));
            avgStats.Width = tmp[0]; stdStats.Width = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.Height));
            avgStats.Height = tmp[0]; stdStats.Height = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.DegreesVar));
            avgStats.DegreesVar = tmp[0]; stdStats.DegreesVar = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.Diameter));
            avgStats.Diameter = tmp[0]; stdStats.Diameter = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.MaxCliqueDistribution));
            avgStats.MaxCliqueDistribution = tmp[0]; stdStats.MaxCliqueDistribution = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.MaxSize));
            avgStats.MaxSize = tmp[0]; stdStats.MaxSize = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.MinSize));
            avgStats.MinSize = tmp[0]; stdStats.MinSize = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.MaxWeight));
            avgStats.MaxWeight = tmp[0]; stdStats.MaxWeight = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.MinWeight));
            avgStats.MinWeight = tmp[0]; stdStats.MinWeight = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.SumSize));
            avgStats.SumSize = tmp[0]; stdStats.SumSize = tmp[1];

            tmp = TreeStatistics.AverageStd(treeStats.Select(t => t.SumWeight));
            avgStats.SumWeight = tmp[0]; stdStats.SumWeight = tmp[1];


            return new List<TreeStatistics>() { avgStats, stdStats };
        }

        public static List<double> AverageStd(IEnumerable<double> values)
        {
            double mean = 0.0;
            double sum = 0.0;
            double stdDev = 0.0;
            int n = 0;
            foreach (double val in values)
            {
                n++;
                double delta = val - mean;
                mean += delta / n;
                sum += delta * (val - mean);
            }

            if (n > 1)
            {
                stdDev = Math.Sqrt(sum / (n - 1));
            }

            return new List<double> { mean, stdDev };
        }

        public static List<long> AverageStd(IEnumerable<long> values)
        {
            long mean = 0;
            long sum = 0;
            long stdDev = 0;
            long n = 0;
            foreach (long val in values)
            {
                n++;
                long delta = val - mean;
                mean += delta / n;
                sum += delta * (val - mean);
            }

            if (n > 1)
            {
                stdDev = (long)Math.Sqrt(sum / (n - 1));
            }

            return new List<long> { mean, stdDev };
        }
    }

    public class Stats
    {
        public Dictionary<string, string> Parameters = new Dictionary<string, string>();
        public Dictionary<string, List<double>> Output = new Dictionary<string, List<double>>();
        public Dictionary<string, List<double>> Times = new Dictionary<string, List<double>>();

        public List<long> Edges = new List<long>();

        public List<TreeStatistics> CliqueTrees { get; set; } = new List<TreeStatistics>();
    }
}