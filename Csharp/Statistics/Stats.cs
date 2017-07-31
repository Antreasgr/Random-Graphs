namespace Statistics
{
    using System.Collections.Generic;

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
    }

    public class Stats
    {
        public Dictionary<string, string> Parameters = new Dictionary<string, string>();
        public Dictionary<string, List<double>> Output = new Dictionary<string, List<double>>();
        public Dictionary<string, List<double>> Times = new Dictionary<string, List<double>>();
        public List<TreeStatistics> CliqueTrees { get; set; } = new List<TreeStatistics>();
    }
}